from funcy import project

from utils import elasticsearch_utils as es_utils
from utils.dictionary_utils import safe_get_in, safe_int_parse
from utils.oms_utils import get_provider_search_tags


def populate_in_stock(item):
    # Item.quantity.count
    quantity = safe_int_parse(safe_get_in(item, ["item_details", "quantity", "available", "count"], 0))
    return quantity > 0


def update_provider_items_with_manual_flags(provider_id, provider_items):
    manually_flagged_items = es_utils.get_all_manually_flagged_items_for_provider(provider_id)
    manually_flagged_dict = {item['id']: item for item in manually_flagged_items}
    for item in provider_items:
        if item["id"] in manually_flagged_dict.keys():
            manually_flagged_item = project(manually_flagged_dict[item["id"]],
                                            ["manual_item_flag", "manual_provider_flag", "manual_seller_flag",
                                             "item_error_tags", "provider_error_tags", "seller_error_tags"
                                             ])
            item.update(manually_flagged_item)
        item["item_flag"] = item["manual_item_flag"] if item.get("manual_item_flag") is not None \
            else item.get("auto_item_flag", False)
        item["seller_flag"] = item["manual_seller_flag"] if item.get("manual_seller_flag") is not None \
            else item.get("auto_seller_flag", False)
        item["provider_flag"] = item["manual_provider_flag"] if item.get("manual_provider_flag") is not None \
            else item.get("auto_provider_flag", False)
        item['in_stock'] = populate_in_stock(item)
    return provider_items


def update_provider_items_and_locations_with_search_tags(provider_id, items, locations):
    provider_search_tags = get_provider_search_tags(provider_id)

    for item in items:
        item["provider_search_tags"] = provider_search_tags
    for loc in locations:
        loc["provider_search_tags"] = provider_search_tags
    return items, locations
