import copy

from config import get_config_by_name
from transformers.first import flatten_full_on_search_payload_to_provider_map
from transformers.second import enrich_items_using_tags_and_categories, enrich_offers_using_serviceabilities, \
    get_unique_locations_from_items
from transformers.third import update_provider_items_with_manual_flags
from transformers.translation import translate_items_into_target_language


def transform_full_on_search_payload_into_default_lang_items(payload):
    provider_map = flatten_full_on_search_payload_to_provider_map(payload)
    final_items = []
    final_offers = []
    final_locations = []

    for pid, v in provider_map.items():
        items = enrich_items_using_tags_and_categories(
            v["items"],
            v["categories"],
            v["serviceabilities"],
            v["provider_error_tags"],
            v["seller_error_tags"],
        )
        locations = get_unique_locations_from_items(items)
        items = update_provider_items_with_manual_flags(pid, items)
        offers = enrich_offers_using_serviceabilities(v["location_offers"], v["serviceabilities"])

        final_items.extend(items)
        final_offers.extend(offers)
        final_locations.extend(locations)

    return final_items, final_offers, final_locations


def transform_full_on_search_payload_into_final_items(payload):
    final_items = []
    default_lang_items, offers, locations = transform_full_on_search_payload_into_default_lang_items(payload)
    final_items.extend(default_lang_items)
    configured_language_list = get_config_by_name("LANGUAGE_LIST")
    for lang in configured_language_list:
        if lang:
            new_items = copy.deepcopy(default_lang_items)
            final_items.extend(translate_items_into_target_language(new_items, lang))
    return final_items, offers, locations
