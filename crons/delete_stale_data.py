from datetime import datetime, timedelta
from elasticsearch.helpers import scan, bulk

from utils.elasticsearch_utils import get_elasticsearch_client


def delete_stale_data():
    # Connect to the Elasticsearch instance
    es = get_elasticsearch_client()
    delete_stale_data_for_given_index(es, "items")
    delete_stale_data_for_given_index(es, "offers")


def delete_stale_data_for_given_index(es, index_name, ttl_in_days=7):
    # Calculate the timestamp for documents older than 7 days
    days_ago = datetime.now() - timedelta(days=ttl_in_days)
    days_ago_str = days_ago.isoformat()

    # Define the query to find documents older than 2 days
    query = {
        "query": {
            "range": {
                "created_at": {
                    "lt": days_ago_str
                }
            }
        }
    }

    # Scan for documents matching the query
    scan_results = scan(client=es, index=index_name, query=query)

    # Delete the documents
    # Prepare bulk delete actions
    bulk_actions = [
        {
            "_op_type": "delete",
            "_index": result["_index"],
            "_id": result["_id"]
        }
        for result in scan_results
    ]

    # Perform bulk delete
    bulk(es, bulk_actions)


if __name__ == '__main__':
    delete_stale_data()
