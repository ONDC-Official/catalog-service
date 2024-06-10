from config import get_config_by_name
from transformers.first import flatten_incr_on_search_payload_to_provider_map_for_items, \
    flatten_incr_on_search_payload_to_provider_map_for_locations, flatten_incr_on_search_payload_to_providers, \
    flatten_incr_on_search_payload_to_provider_map_for_offers
from transformers import queries
from funcy import project

from transformers.translation import translate_items_into_configured_languages


def transform_incr_on_search_payload_into_final_items(payload):
    catalog = payload["message"]["catalog"]
    bpp_providers = catalog.get("bpp/providers", [])
    bpp_provider_first = bpp_providers[0]
    if "items" in bpp_provider_first:
        return get_item_objects_for_item_update(payload), []
    elif "locations" in bpp_provider_first:
        return get_item_objects_for_location_update(payload), []
    elif "offers" in bpp_provider_first:
        return [], get_offer_objects_for_offers_update(payload)
    else:
        return get_item_objects_for_provider_update(payload), []


def get_item_objects_for_item_update_for_default_language(payload):
    item_objects = []
    bpp_id = payload["context"]["bpp_id"]
    provider_map = flatten_incr_on_search_payload_to_provider_map_for_items(payload)
    for provider_id, provider_items in provider_map.items():
        for i in provider_items:
            db_item = queries.get_item_with_given_id(i['id'])
            if db_item is None:
                item_details = i["item_details"]
                db_item = queries.get_items_for_given_details(
                    bpp_id=bpp_id,
                    provider_id=provider_id,
                    item_type=i["type"],
                    variant_group_id=f'{provider_id}_{item_details.get("parent_item_id")}',
                )[0]
            db_item.update(project(i, ["id", "local_id", "type", "attributes", "item_details", "created_at"]))
            item_objects.append(db_item)

    return item_objects


def get_item_objects_for_item_update(payload):
    final_items = []
    default_lang_items = get_item_objects_for_item_update_for_default_language(payload)
    final_items.extend(default_lang_items)
    configured_language_list = get_config_by_name("LANGUAGE_LIST")
    for lang in configured_language_list:
        final_items.extend(translate_items_into_configured_languages(default_lang_items, lang))
    return final_items


def get_item_objects_for_location_update(payload):
    item_objects = []
    bpp_id = payload["context"]["bpp_id"]
    provider_map = flatten_incr_on_search_payload_to_provider_map_for_locations(payload)
    for provider_id, locations in provider_map.items():
        for lo in locations:
            db_items = queries.get_items_for_given_details(
                bpp_id=bpp_id,
                provider_id=provider_id,
                location_id=f'{provider_id}_{lo.get("id")}',
            )
            for i in db_items:
                i["location_details"]["time"] = lo["time"]
            item_objects.extend(db_items)
    return item_objects


def get_offer_objects_for_offers_update(payload):
    offer_objects = []
    bpp_id = payload["context"]["bpp_id"]
    provider_map = flatten_incr_on_search_payload_to_provider_map_for_offers(payload)
    for provider_id, location_offers in provider_map.items():
        for i in location_offers:
            db_offer = queries.get_offers_for_given_details(
                bpp_id=bpp_id,
                provider_id=provider_id,
                location_id=f'{provider_id}_{i["location_id"]}',
            )[0]
            db_offer.update(project(i, ["id", "local_id", "descriptor", "time", "tags", "created_at"]))
            offer_objects.append(db_offer)

    return offer_objects


def get_item_objects_for_provider_update(payload):
    item_objects = []
    bpp_id = payload["context"]["bpp_id"]
    providers = flatten_incr_on_search_payload_to_providers(payload)
    for p in providers:
        db_items = queries.get_items_for_given_details(
            bpp_id=bpp_id,
            provider_id=p["id"],
        )
        for i in db_items:
            i["provider_details"]["time"] = p["time"]
        item_objects.extend(db_items)
    return item_objects
