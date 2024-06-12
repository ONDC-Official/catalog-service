import json
import os

from utils import elasticsearch_utils as es_utils


def make_query_object_must_statements(must_statements):
    return {
        "query": {
            "bool": {
                "must": must_statements
            }
        }
    }


def get_item_with_given_id(item_id, langauge='en'):
    must_statements = [{"term": {"id": item_id}}, {"term": {"language": langauge}}]
    resp = es_utils.search_documents("items", make_query_object_must_statements(must_statements))
    resp_items = resp["hits"]["hits"]
    if len(resp_items) > 0:
        return resp_items[0]["_source"]
    else:
        return None


def get_offer_with_given_id(offer_id, langauge='en'):
    must_statements = [{"term": {"id": offer_id}}, {"term": {"language": langauge}}]
    resp = es_utils.search_documents("offers", make_query_object_must_statements(must_statements))
    resp_items = resp["hits"]["hits"]
    if len(resp_items) > 0:
        return resp_items[0]["_source"]
    else:
        return None


def get_items_for_given_details(bpp_id, provider_id, location_id=None, item_type="item", variant_group_id=None, customisation_group_id=None):
    must_statements = [
        {"term": {"bpp_details.bpp_id": bpp_id}},
        {"term": {"provider_details.id": provider_id}},
        {"term": {"type": item_type}},
    ]
    must_statements.append({"term": {"location_details.id": location_id}}) if location_id else None
    must_statements.append({"term": {"variant_group.id": variant_group_id}}) if variant_group_id else None
    must_statements.append({"term": {"customisation_group.id": customisation_group_id}}) if customisation_group_id else None

    resp = es_utils.search_documents("items", make_query_object_must_statements(must_statements))
    resp_items = resp["hits"]["hits"]
    return [i["_source"] for i in resp_items]


def get_offers_for_given_details(bpp_id, provider_id, location_id):
    must_statements = [
        {"term": {"bpp_details.bpp_id": bpp_id}},
        {"term": {"provider_details.id": provider_id}},
        {"term": {"location_details.id": location_id}},
    ]

    resp = es_utils.search_documents("offers", make_query_object_must_statements(must_statements))
    resp_items = resp["hits"]["hits"]
    return [i["_source"] for i in resp_items]


def search_items(lat, lng, search_str=None):
    query_obj = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "item_details.descriptor.name": search_str
                    }
                },
                "should": [
                    {
                        "match": {
                            "location_details.type.keyword": "pan"
                        }
                    },
                    {
                        "geo_shape": {
                            "location_details.polygons": {
                                "shape": {
                                    "type": "point",
                                    "coordinates": [lat, lng]
                                }
                            }
                        }
                    }
                ]
            }
        }
    }

    resp = es_utils.search_documents("items", query_obj)
    resp_items = resp["hits"]["hits"]
    return [i["_source"] for i in resp_items]


def get_providers(lat, lng, size=10):
    query_obj = {
        "query": {
            "bool": {
                "filter": {
                    "geo_shape": {
                        "location_details.polygons": {
                            "shape": {
                                "type": "point",
                                "coordinates": [lat, lng]
                            }
                        }
                    }
                }
            }
        },
        "aggs": {
            "unique_providers": {
                "terms": {
                    "field": "provider_details.id",  # Assuming 'provider' is the field name and it's not analyzed
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
    resp = es_utils.search_documents("items", query_obj)
    unique_providers = []
    for bucket in resp['aggregations']['unique_providers']['buckets']:
        provider_details = [i["_source"]['provider_details'] for i in bucket['products']['hits']['hits']][0]
        unique_providers.append(provider_details)

    return unique_providers


def get_attributes(domain):
    query_obj = {
        "_source": ["attributes"],
        "size": 1000,
        "query": {
            "term": {
                "context.domain": domain
            }
        }
    }
    resp = es_utils.search_documents_with_scroll("items", query_obj)

    scroll_id = resp["_scroll_id"]
    distinct_keys = set()

    # Scroll through all documents
    while len(resp["hits"]["hits"]):
        for hit in resp["hits"]["hits"]:
            attributes = hit["_source"].get("attributes", {})
            distinct_keys.update(attributes.keys())

        # Get the next batch of documents
        resp = es_utils.get_scroll_documents(scroll_id)

    # Clear the scroll context
    es_utils.clear_scroll(scroll_id)

    return list(distinct_keys)


def get_customisation_items_from_customisation_groups(customisation_group_ids):
    query_obj = {
        "query": {
            "bool": {
                "must": {
                    "terms": {
                        "customisation_group_id": customisation_group_ids
                    }
                }
            }
        }
    }

    resp = es_utils.search_documents("items", query_obj)
    resp_items = resp["hits"]["hits"]
    return [i["_source"] for i in resp_items]


if __name__ == '__main__':
    os.environ["ENV"] = "dev"
    print(get_attributes("ONDC:RET12"))
    # print(get_item_with_given_id("sellerNPFashion.com_ONDC:RET12_P1_I1", 'hi'))
    # print(json.dumps(dict(es_utils.get_index_mapping("items"))))
    # [print(json.dumps(s)) for s in search_items(12.967555, 77.749666, "allen1")]
    # [print(p) for p in get_providers(13.0520609, 77.7948985, 30)]
