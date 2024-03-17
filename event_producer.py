import os
import json

from config import get_config_by_name
from logger.custom_logging import log
from services.mongo_service import dump_on_search_payload
from utils.rabbitmq_utils import publish_message_to_queue, open_connection_and_channel_if_not_already_open, \
    declare_queue

filepath = "/Users/aditya/Projects/ondc-sdk/catalog-service/resources/on_search_with_attributes.json"
with open(filepath) as f:
    json_payload = json.load(f)
    doc_id = dump_on_search_payload(json_payload)
    message = {
        "doc_id": str(doc_id),
        "request_type": "full",
    }
    rabbitmq_connection, rabbitmq_channel = open_connection_and_channel_if_not_already_open(None, None)
    queue_name = get_config_by_name('RABBITMQ_QUEUE_NAME')
    declare_queue(rabbitmq_channel, queue_name)
    log(f"Sending message with payload : {json_payload} to {queue_name}")
    publish_message_to_queue(rabbitmq_channel, exchange='', routing_key=queue_name, body=json.dumps(message))
