from config import get_config_by_name
from utils.mongo_utils import get_mongo_collection, collection_find_one


def validate_search_request_validity(payload):
    if get_config_by_name("IS_TEST"):
        return None
    context = payload["context"]
    collection = get_mongo_collection("request_dump")
    filter_criteria = {"action": "search", "request.context.domain": context["domain"],
                       "request.context.transaction_id": context["transaction_id"]}
    search_request = collection_find_one(collection, filter_criteria, keep_created_at=True)
    if search_request:
        minutes_diff = (payload['created_at'] - search_request['created_at']).total_seconds() // 60
        if minutes_diff < 30:
            return None
    return "No search request was made with given domain and transaction_id in last 30 minutes!"