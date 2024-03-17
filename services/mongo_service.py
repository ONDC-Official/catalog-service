from datetime import datetime

from utils.mongo_utils import get_mongo_collection, collection_insert_one


def dump_on_search_payload(payload):
    collection = get_mongo_collection('on_search_dump')
    payload["created_at"] = datetime.utcnow()
    payload["status"] = "PENDING"
    return collection_insert_one(collection, payload)


def update_on_search_dump_status(object_id, status, response_time=None):
    collection = get_mongo_collection('on_search_dump')
    filter_criteria = {"_id": object_id}
    value = {"status": status}
    if response_time:
        value["response_time"] = response_time
    collection.update_one(filter_criteria, {'$set': value})


# def get_last_search_dump_timestamp(transaction_id):
#     search_collection = get_mongo_collection('request_dump')
#     query_object = {"action": "search", "request.context.transaction_id": transaction_id}
#     catalog = collection_find_one_with_sort(search_collection, query_object, "created_at")
#     return catalog['created_at'] if catalog else None
#
#
# def get_last_request_dump(request_type, transaction_id):
#     search_collection = get_mongo_collection('request_dump')
#     query_object = {"action": request_type, "request.context.transaction_id": transaction_id}
#     catalog = collection_find_one_with_sort(search_collection, query_object, "created_at")
#     if catalog:
#         catalog.pop("created_at")
#         return catalog
#     else:
#         return {"error": "No request found for given type and transaction_id!"}, 400