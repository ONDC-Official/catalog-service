import json

from pika.exceptions import AMQPConnectionError
from retry import retry

from config import get_config_by_name
from event_producer import publish_message
from transformers.translation import translate_items_into_target_language
from utils.redis_utils import init_redis_cache
from utils.rabbitmq_utils import create_channel, declare_queue, open_connection, consume_message


def consume_fn(message_string):
    message = json.loads(message_string)
    es_dumper_queue = get_config_by_name('ES_DUMPER_QUEUE_NAME')
    if message["index"] == "items":
        translated_items = translate_items_into_target_language(message["data"], message["lang"])
        publish_message(es_dumper_queue, {"index": "items", "data": translated_items})


@retry(AMQPConnectionError, delay=5, jitter=(1, 3))
def run_consumer():
    init_redis_cache()
    queue_name = get_config_by_name('TRANSLATOR_QUEUE_NAME')
    connection = open_connection()
    channel = create_channel(connection)
    declare_queue(channel, queue_name)
    consume_message(connection, channel, queue_name=queue_name, consume_fn=consume_fn)


if __name__ == "__main__":
    run_consumer()
