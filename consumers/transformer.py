import json
import time

from bson.objectid import ObjectId
from elasticsearch.helpers import BulkIndexError
from pika.exceptions import AMQPConnectionError
from retry import retry

from config import get_config_by_name
from event_producer import publish_message
from logger.custom_logging import log, log_error
from services.mongo_service import update_on_search_dump_status
from transformers.full_catalog import transform_full_on_search_payload_into_default_lang_items
from transformers.incr_catalog import transform_incr_on_search_payload_into_final_items
from utils.elasticsearch_utils import init_elastic_search
from utils.json_utils import clean_nones, datetime_serializer
from utils.mongo_utils import get_mongo_collection, collection_find_one, init_mongo_database
from utils.rabbitmq_utils import create_channel, declare_queue, consume_message, open_connection


def split_docs_into_batches(docs, max_size_mbs):
    batches = []
    current_batch = []
    current_size = 0

    for doc in docs:
        doc_str = json.dumps(doc, default=datetime_serializer)
        doc_size = len(doc_str.encode('utf-8'))
        log(f"doc size: {doc_size}")

        if current_size + doc_size > (max_size_mbs * 1024 * 1024):
            batches.append(current_batch)
            current_batch = [doc]
            current_size = doc_size
        else:
            current_batch.append(doc)
            current_size += doc_size

    if current_batch:
        batches.append(current_batch)

    return batches


def publish_documents_splitting_per_rabbitmq_limit(queue, index, docs, lang=None):
    if len(docs) > 0:
        current_batch = []
        current_size = 0

        for doc in docs:
            doc_str = json.dumps(doc, default=datetime_serializer)
            doc_size = len(doc_str.encode('utf-8'))

            if current_size + doc_size > (20 * 1024 * 1024):
                message = {"index": index, "data": current_batch}
                message.update({"lang": lang}) if lang else None
                publish_message(queue, message)
                # batches.append(current_batch)
                current_batch = [doc]
                current_size = doc_size
            else:
                current_batch.append(doc)
                current_size += doc_size

        if current_batch:
            message = {"index": index, "data": current_batch}
            message.update({"lang": lang}) if lang else None
            publish_message(queue, message)

        # batches = split_docs_into_batches(docs, 10)
        # for b in batches:
        #     message = {"index": index, "data": b}
        #     message.update({"lang": lang}) if lang else None
        #     publish_message(queue, message)


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
            on_search_payload = clean_nones(on_search_payload)
            on_search_payload.pop("id", None)
            if payload["request_type"] == "full":
                update_on_search_dump_status(doc_id, "IN-PROGRESS", None)
                items, offers = transform_full_on_search_payload_into_default_lang_items(on_search_payload)
                es_dumper_queue = get_config_by_name('ES_DUMPER_QUEUE_NAME')
                publish_documents_splitting_per_rabbitmq_limit(es_dumper_queue, "items", items)
                publish_documents_splitting_per_rabbitmq_limit(es_dumper_queue, "offers", offers)
                update_on_search_dump_status(doc_id, "FINISHED")

                translator_queue = get_config_by_name('TRANSLATOR_QUEUE_NAME')
                for lang in get_config_by_name("LANGUAGE_LIST"):
                    if lang:
                        publish_documents_splitting_per_rabbitmq_limit(translator_queue, "items", items, lang=lang)

            elif payload["request_type"] == "inc":
                update_on_search_dump_status(doc_id, "IN-PROGRESS")
                items, offers = transform_incr_on_search_payload_into_final_items(on_search_payload)
                es_dumper_queue = get_config_by_name('ES_DUMPER_QUEUE_NAME')
                publish_documents_splitting_per_rabbitmq_limit(es_dumper_queue, "items", items)
                publish_documents_splitting_per_rabbitmq_limit(es_dumper_queue, "offers", offers)
                update_on_search_dump_status(doc_id, "FINISHED")
        else:
            log_error(f"On search payload was not found for {doc_id}!")
            update_on_search_dump_status(doc_id, "FAILED", f"On search payload was not found for {doc_id}!")
    except BulkIndexError as e:
        log_error(f"Got error while adding in elasticsearch!")
        update_on_search_dump_status(doc_id, "FAILED", e.errors[0]['index']['error']['reason'])
    except Exception as e:
        log_error(f"Something went wrong with consume function - {e}!")
        update_on_search_dump_status(doc_id, "FAILED", str(e)) if doc_id else None


@retry(AMQPConnectionError, delay=5, jitter=(1, 3))
def run_consumer():
    init_mongo_database()
    queue_name = get_config_by_name('ELASTIC_SEARCH_QUEUE_NAME')
    connection = open_connection()
    channel = create_channel(connection)
    declare_queue(channel, queue_name)
    consume_message(connection, channel, queue_name=queue_name,
                    consume_fn=consume_fn)


if __name__ == "__main__":
    run_consumer()
