from datetime import datetime

from utils.mongo_utils import get_mongo_collection, collection_insert_one


def dump_on_search_payload(payload):
    collection = get_mongo_collection('on_search_dump')
    payload["created_at"] = datetime.utcnow()
    payload["status"] = "PENDING"
    return collection_insert_one(collection, payload)


def update_on_search_dump_status(object_id, status, error=None, response_time=None):
    collection = get_mongo_collection('on_search_dump')
    filter_criteria = {"_id": object_id}
    value = {"status": status}
    if error:
        value["error"] = error
    if response_time:
        value["response_time"] = response_time
    collection.update_one(filter_criteria, {'$set': value})
