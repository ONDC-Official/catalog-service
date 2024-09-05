import functools
import threading

import pika


from config import get_config_by_name
from logger.custom_logging import log, log_error

global_connection, global_channel = None, None


def open_connection_and_channel_if_not_already_open():
    global global_connection, global_channel
    if global_connection and global_connection.is_open:
        log("Getting old connection and channel")
        return global_connection, global_channel
    else:
        log("Getting new connection and channel")
        global_connection = open_connection()
        global_channel = create_channel(global_connection)
        return global_connection, global_channel


def open_connection():
    rabbitmq_host = get_config_by_name('RABBITMQ_HOST')
    rabbitmq_creds = get_config_by_name('RABBITMQ_CREDS')
    if rabbitmq_creds:
        credentials = pika.PlainCredentials(get_config_by_name('RABBITMQ_USERNAME'),
                                            get_config_by_name('RABBITMQ_PASSWORD'))
        return pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host, credentials=credentials))
    else:
        return pika.BlockingConnection(pika.ConnectionParameters(host=rabbitmq_host))


def close_connection(connection):
    connection.close()


def create_channel(connection):
    channel = connection.channel()
    channel.basic_qos(prefetch_count=get_config_by_name('CONSUMER_MAX_WORKERS', 10))
    return channel


def declare_queue(channel, queue_name):
    # channel.exchange_declare("test-x", exchange_type="x-delayed-message", arguments={"x-delayed-type": "direct"})
    channel.queue_declare(queue=queue_name)


# @retry(3, errors=StreamLostError)
def publish_message_to_queue(channel, exchange, routing_key, body, properties=None):
    channel.basic_publish(exchange=exchange, routing_key=routing_key, body=body, properties=properties)


def consume_message(connection, channel, queue_name, consume_fn):
    def callback(ch, delivery_tag, body):
        try:
            channel.basic_ack(delivery_tag)
            log(f"Ack message for Delivery tag: {delivery_tag} !")
        except:
            log_error(f"Something went wrong for {delivery_tag} !")

    def do_work(delivery_tag, body):
        thread_id = threading.get_ident()
        log(f'Thread id: {thread_id} Delivery tag: {delivery_tag}')
        cb = functools.partial(callback, channel, delivery_tag, body)

        try:
            consume_fn(body)
        except Exception as e:
            log_error(f"Error processing message with Thread id: {thread_id} Delivery tag: {delivery_tag}: {e}")

        if connection and connection.is_open:
            connection.add_callback_threadsafe(cb)
        else:
            log_error("Connection is closed. Cannot add callback.")

    def on_message(ch, method_frame, header_frame, body):
        delivery_tag = method_frame.delivery_tag
        if len(ch.consumer_tags) == 0:
            log_error("Nobody is listening. Stopping the consumer!")
            return
        t = threading.Thread(target=do_work, args=(delivery_tag, body))
        t.start()
        threads.append(t)

    threads = []
    on_message_callback = functools.partial(on_message)

    channel.basic_consume(queue=queue_name, on_message_callback=on_message_callback, auto_ack=False)
    log('Waiting for messages:')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        channel.stop_consuming()

    # Wait for all to complete
    for thread in threads:
        thread.join()

    connection.close()
