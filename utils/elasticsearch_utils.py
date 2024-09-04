import json
import os

from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk, BulkIndexError

from utils.hash_utils import get_md5_hash
from logger.custom_logging import log, log_error
from config import get_config_by_name

elasticsearch_client = None


def get_elasticsearch_client() -> Elasticsearch:
    global elasticsearch_client
    if elasticsearch_client is None:
        elasticsearch_client = Elasticsearch(get_config_by_name("ELASTIC_SEARCH_URL"), timeout=60)
    return elasticsearch_client


def get_all_indexes():
    client = get_elasticsearch_client()
    return client.indices


def get_index_mapping(index_name):
    client = get_elasticsearch_client()
    return client.indices.get_mapping(index=index_name)


def init_elastic_search():
    client = get_elasticsearch_client()
    init_es_index(client, "items")
    init_es_index(client, "offers")
    init_es_index(client, "locations")
    init_es_index(client, "manually_flagged_items")


def init_es_index(client, index_name):
    if client.indices.exists(index=index_name):
        log(f"Index '{index_name}' already exists.")
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        items_mapping_json_path = os.path.join(current_dir, f'../mappings/{index_name}_mappings.json')
        with open(items_mapping_json_path, 'r') as json_file:
            items_mapping_json = json.load(json_file)

        response = client.indices.create(index=index_name, body=items_mapping_json)

        # Check if the index creation was successful
        if response['acknowledged']:
            print(f"Index '{index_name}' created successfully with mapping.")
        else:
            print(f"Failed to create index '{index_name}'.")


# Define a generator function to yield Elasticsearch index operations for each document
def generate_actions(index_name, documents):
    for doc in documents:
        # Use the ID + language as the Elasticsearch document ID
        yield {
            "_index": index_name,
            "_id": get_md5_hash(f"{doc['id']}_{doc['language']}"),
            "_source": doc
        }


def add_documents_to_index(index_name, documents):
    client = get_elasticsearch_client()
    try:
        if documents is not None and len(documents) > 0:
            log(f"Adding {len(documents)} {index_name}")
            success, _ = bulk(client, generate_actions(index_name, documents),
                              chunk_size=get_config_by_name("BULK_CHUNK_SIZE"))
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


def search_documents_with_scroll(index_name, search_query, scroll="2m"):
    client = get_elasticsearch_client()
    try:
        response = client.search(index=index_name, body=search_query, scroll=scroll)
        return response
    except Exception as e:
        print("Error:", e)


def get_scroll_documents(scroll_id, scroll="2m"):
    client = get_elasticsearch_client()
    try:
        response = client.scroll(scroll_id=scroll_id, scroll=scroll)
        return response
    except Exception as e:
        print("Error:", e)


def clear_scroll(scroll_id):
    client = get_elasticsearch_client()
    try:
        response = client.clear_scroll(scroll_id=scroll_id)
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


def get_all_manually_flagged_items_for_provider(provider_id):
    items = []
    # Define the query to match provider_details.id
    query = {
        "query": {
            "term": {
                "provider_details.id": provider_id  # Replace with the actual provider ID
            }
        }
    }
    es = get_elasticsearch_client()
    # Initialize the scroll
    response = es.search(
        index="manually_flagged_items",
        body=query,
        scroll='2m',  # Scroll context will be kept alive for 2 minutes
        size=1000     # Adjust the batch size as needed
    )

    # Extract the scroll ID and initial batch of results
    scroll_id = response['_scroll_id']
    hits = response['hits']['hits']

    # Collect all results
    all_hits = []
    while hits:
        all_hits.extend(hits)

        # Make a request to fetch the next batch of results
        response = es.scroll(
            scroll_id=scroll_id,
            scroll='2m'  # Scroll context will be kept alive for 2 minutes
        )

        # Update the scroll ID and hits
        scroll_id = response['_scroll_id']
        hits = response['hits']['hits']

    # Optionally clear the scroll context to free resources
    es.clear_scroll(scroll_id=scroll_id)

    # Process the results
    for hit in all_hits:
        items.append(hit["_source"])
    return items


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
