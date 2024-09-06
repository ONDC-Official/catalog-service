import json
import os

from config import get_config_by_name
from logger.custom_logging import log
from services.mongo_service import dump_on_search_payload
from utils.json_utils import datetime_serializer
from utils.rabbitmq_utils import publish_message_to_queue, open_connection, create_channel, \
    close_channel_and_connection, declare_queue


def publish_message_for_transform(file_path, request_type):
    with open(file_path) as f:
        json_payload = json.load(f)
        doc_id = dump_on_search_payload(json_payload)
        message = {
            "doc_id": str(doc_id),
            "request_type": request_type,
        }
        rabbitmq_connection = open_connection()
        rabbitmq_channel = create_channel(rabbitmq_connection)
        queue_name = get_config_by_name('ELASTIC_SEARCH_QUEUE_NAME')
        declare_queue(rabbitmq_channel, queue_name)
        log(f"Sending message with payload : {json_payload} to {queue_name}")
        publish_message_to_queue(rabbitmq_channel, exchange='', routing_key=queue_name, body=json.dumps(message))
        close_channel_and_connection(rabbitmq_channel, rabbitmq_connection)


def publish_message(rabbitmq_channel, queue_name, message):
    log(f"Sending message for {message['index']} to {queue_name}")
    publish_message_to_queue(rabbitmq_channel, exchange='', routing_key=queue_name,
                             body=json.dumps(message, default=datetime_serializer))


if __name__ == '__main__':
    current_dir = os.path.dirname(os.path.abspath(__file__))
    local_filepath = os.path.join(current_dir, f'resources/simple_on_search.json')
    req_type = "full"
    publish_message_for_transform(local_filepath, req_type)
