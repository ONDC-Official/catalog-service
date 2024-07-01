import json
import time

from bson.objectid import ObjectId
from pika.exceptions import AMQPConnectionError
from retry import retry

from config import get_config_by_name
from logger.custom_logging import log, log_error
from services.mongo_service import update_on_search_dump_status
from transformers.full_catalog import transform_full_on_search_payload_into_default_lang_items, transform_full_on_search_payload_into_final_items
from transformers.incr_catalog import transform_incr_on_search_payload_into_final_items
from utils.elasticsearch_utils import add_documents_to_index, init_elastic_search
from utils.redis_utils import init_redis_cache
from utils.mongo_utils import get_mongo_collection, collection_find_one, init_mongo_database
from utils.rabbitmq_utils import create_channel, declare_queue, consume_message, open_connection


def consume_fn(message_string):
    doc_id = None
    try:
        time.sleep(2)
        payload = json.loads(message_string)
        log(f"Got the payload {payload}!")

        doc_id = ObjectId(payload["doc_id"])
        collection = get_mongo_collection('on_search_dump')
        on_search_payload = collection_find_one(collection, {"_id": doc_id}, keep_created_at=True)
        if on_search_payload:
            on_search_payload.pop("id", None)
            if payload["request_type"] == "full":
                # search_timestamp = get_last_search_dump_timestamp(on_search_payload["context"]["transaction_id"])
                # if search_timestamp:
                # response_time = (on_search_payload["created_at"] - search_timestamp).seconds
                update_on_search_dump_status(doc_id, "IN-PROGRESS", None)
                # else:
                #     log_error(f"No search request found for given {on_search_payload['context']}")
                #     update_on_search_dump_status(doc_id, "IN-PROGRESS")
                items, offers = transform_full_on_search_payload_into_final_items(on_search_payload)
                add_documents_to_index("items", items)
                add_documents_to_index("offers", offers)
                update_on_search_dump_status(doc_id, "FINISHED")
            elif payload["request_type"] == "inc":
                update_on_search_dump_status(doc_id, "IN-PROGRESS")
                items, offers = transform_incr_on_search_payload_into_final_items(on_search_payload)
                add_documents_to_index("items", items)
                add_documents_to_index("offers", offers)
                update_on_search_dump_status(doc_id, "FINISHED")
        else:
            log_error(f"On search payload was not found for {doc_id}!")
            update_on_search_dump_status(doc_id, "FAILED")
    except Exception as e:
        log_error(f"Something went wrong with consume function - {e}!")
        update_on_search_dump_status(doc_id, "FAILED") if doc_id else None


@retry(AMQPConnectionError, delay=5, jitter=(1, 3))
def run_consumer():
    init_mongo_database()
    init_elastic_search()
    init_redis_cache()
    queue_name = get_config_by_name('ELASTIC_SEARCH_QUEUE_NAME')
    connection = open_connection()
    channel = create_channel(connection)
    declare_queue(channel, queue_name)
    consume_message(connection, channel, queue_name=queue_name,
                    consume_fn=consume_fn)


if __name__ == "__main__":
    run_consumer()
