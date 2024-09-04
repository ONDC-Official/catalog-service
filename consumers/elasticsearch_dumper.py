import json

from pika.exceptions import AMQPConnectionError
from retry import retry

from config import get_config_by_name
from utils.elasticsearch_utils import init_elastic_search, add_documents_to_index
from utils.rabbitmq_utils import create_channel, declare_queue, open_connection, consume_message


def consume_fn(message_string):
    message = json.loads(message_string)
    if message["index"] == "items":
        add_documents_to_index("items", message["data"])
    elif message["index"] == "offers":
        add_documents_to_index("offers", message["data"])
    elif message["index"] == "locations":
        add_documents_to_index("locations", message["data"])


@retry(AMQPConnectionError, delay=5, jitter=(1, 3))
def run_consumer():
    init_elastic_search()
    queue_name = get_config_by_name('ES_DUMPER_QUEUE_NAME')
    connection = open_connection()
    channel = create_channel(connection)
    declare_queue(channel, queue_name)
    consume_message(connection, channel, queue_name=queue_name, consume_fn=consume_fn)


if __name__ == "__main__":
    run_consumer()
