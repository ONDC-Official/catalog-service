from pymongo import MongoClient

from config import get_config_by_name
from logger.custom_logging import log

mongo_client = None
mongo_db = None


def init_mongo_database():
    global mongo_client, mongo_db
    if mongo_client is not None and mongo_db is not None:
        return
    database_url = get_config_by_name('MONGO_DATABASE_URL')
    database_name = get_config_by_name('MONGO_DATABASE_NAME')
    mongo_client = MongoClient(database_url)
    mongo_db = mongo_client[database_name]
    log(f"Connection string to database is {database_url}!")


def get_mongo_collection(collection_name):
    # check if database is initialized
    global mongo_client, mongo_db
    if mongo_client is None or mongo_db is None:
        init_mongo_database()
    return mongo_db[collection_name]


def collection_find_one(mongo_collection, query_object, keep_created_at=False):
    if mongo_collection.name == "on_search_items":
        catalog = mongo_collection.find_one(query_object, {})
    else:
        catalog = mongo_collection.find_one(query_object)
    if catalog:
        catalog.pop('_id')
        if not keep_created_at:
            catalog.pop('created_at', None)
    return catalog


def collection_insert_one(mongo_collection, entry):
    resp = mongo_collection.insert_one(entry)
    return resp.inserted_id
