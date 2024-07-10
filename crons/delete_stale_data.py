from datetime import datetime, timedelta
from elasticsearch.helpers import scan, bulk

from utils.elasticsearch_utils import get_elasticsearch_client


def delete_stale_data():
    # Connect to the Elasticsearch instance
    es = get_elasticsearch_client()

    # Index name
    index_name = 'items'

    # Calculate the timestamp for documents older than 7 days
    two_days_ago = datetime.now() - timedelta(days=7)
    two_days_ago_str = two_days_ago.isoformat()

    # Define the query to find documents older than 2 days
    query = {
        "query": {
            "range": {
                "created_at": {
                    "lt": two_days_ago_str
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
