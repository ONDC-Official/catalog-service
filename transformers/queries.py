from utils import elasticsearch_utils as es_utils


def make_query_object_must_statements(must_statements):
    return {
        "query": {
            "bool": {
                "must": must_statements
            }
        }
    }


def get_item_with_given_id(item_id):
    must_statements = [{"term": {"_id": item_id}}]
    resp = es_utils.search_documents("items", make_query_object_must_statements(must_statements))
    resp_items = resp["hits"]["hits"]
    if len(resp_items) > 0:
        return resp_items[0]["_source"]
    else:
        return None


def get_items_for_given_details(bpp_id, provider_id, location_id=None, item_type="item", variant_group_id=None, customisation_group_id=None):
    must_statements = [
        {"term": {"bpp_details.bpp_id.keyword": bpp_id}},
        {"term": {"provider_details.id.keyword": provider_id}},
        {"term": {"type.keyword": item_type}},
    ]
    must_statements.append({"term": {"location_details.id.keyword": location_id}}) if location_id else None
    must_statements.append({"term": {"variant_group.id.keyword": variant_group_id}}) if variant_group_id else None
    must_statements.append({"term": {"customisation_group.id.keyword": customisation_group_id}}) if customisation_group_id else None

    resp = es_utils.search_documents("items", make_query_object_must_statements(must_statements))
    resp_items = resp["hits"]["hits"]
    return [i["_source"] for i in resp_items]


if __name__ == '__main__':
    print(get_item_with_given_id("sellerNPFashion.com_P1_I9"))
    # [print(p) for p in get_items_for_given_details("sellerNPFashion.com", "P1")]