from transformers.first import flatten_on_search_payload_to_provider_map
from transformers.second import enrich_items_using_tags_and_categories


def transform_on_search_payload_into_final_items(payload):
    provider_map = flatten_on_search_payload_to_provider_map(payload)
    final_items = []

    for pid, v in provider_map.items():
        final_items.extend(enrich_items_using_tags_and_categories(
            v["items"],
            v["categories"],
            v["serviceabilities"],
        ))

    return final_items
