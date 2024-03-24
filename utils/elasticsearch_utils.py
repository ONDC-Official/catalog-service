from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError

from logger.custom_logging import log, log_error
from config import get_config_by_name

elasticsearch_client = None


def get_elasticsearch_client() -> Elasticsearch:
    global elasticsearch_client
    if elasticsearch_client is None:
        elasticsearch_client = Elasticsearch(get_config_by_name("ELASTIC_SEARCH_URL"))
    return elasticsearch_client


def get_all_indexes():
    client = get_elasticsearch_client()
    return client.indices


# def get_task_status(task_id):
#     client = get_elasticsearch_client()
#     return client.get_task(task_id)


# Define a generator function to yield Elasticsearch index operations for each document
def generate_actions(index_name, documents):
    for doc in documents:
        yield {
            "_index": index_name,
            "_id": doc["id"],  # Use the document ID as the Elasticsearch document ID
            "_source": doc
        }


def add_documents_to_index(index_name, documents):
    client = get_elasticsearch_client()
    try:
        if documents is not None and len(documents) > 0:
            success, _ = bulk(client, generate_actions(index_name, documents))
            log(success)
            log("Documents added to index")
    except BulkIndexError as e:
        # Handle document write errors
        for error in e.errors:
            log_error("Error occurred for document ID:", error['index']['_id'])
            log_error("Error message:", error['index']['error']['reason'])
        raise e


def delete_index(index_name):
    client = get_elasticsearch_client()
    if client.indices.exists(index=index_name):
        # Delete the index
        response = client.indices.delete(index=index_name)

        # Check if the deletion was successful
        if response.get('acknowledged', False):
            log(f"Index '{index_name}' deleted successfully.")
        else:
            log_error(f"Failed to delete index '{index_name}'.")
    else:
        log_error(f"Index '{index_name}' does not exist.")


def search_documents(index_name, search_query):
    client = get_elasticsearch_client()
    try:
        response = client.search(index=index_name, body=search_query)
        return response
    except Exception as e:
        print("Error:", e)


def search_products_for_unique_provider(size=10):
    client = get_elasticsearch_client()
    aggregation_query = {
        "aggs": {
            "unique_providers": {
                "terms": {
                    "field": "provider.keyword",  # Assuming 'provider' is the field name and it's not analyzed
                    "size": size  # Adjust the size as needed, this will return up to 10000 unique providers
                },
                "aggs": {
                    "products": {
                        "top_hits": {
                            "size": 1
                        }
                    }
                }
            }
        }
    }
    try:
        response = client.search(index="products", body=aggregation_query)
        unique_providers = []
        for bucket in response['aggregations']['unique_providers']['buckets']:
            provider_details = {
                'provider': bucket['key'],
                'products': bucket['products']['hits']['hits']
            }
            unique_providers.append(provider_details)

        return unique_providers
    except Exception as e:
        log_error("Error:", e)


if __name__ == '__main__':
    resp = search_documents("items", {
        "query": {
            "bool": {
                "must": [
                    {
                        "term": {
                            "item_details.parent_item_id.keyword": "V1"
                        }
                    }
                ]
            }
        }
    })
    resp_items = resp["hits"]["hits"]
    [print(i["_source"]) for i in resp_items]
