from transformers.first import flatten_incr_on_search_payload_to_provider_map_for_items, \
    flatten_incr_on_search_payload_to_provider_map_for_locations, flatten_incr_on_search_payload_to_providers
from transformers import queries
from funcy import project


def transform_incr_on_search_payload_into_final_items(payload):
    catalog = payload["message"]["catalog"]
    bpp_providers = catalog.get("bpp/providers", [])
    bpp_provider_first = bpp_providers[0]
    if "items" in bpp_provider_first:
        return get_item_objects_for_item_update(payload)
    elif "locations" in bpp_provider_first:
        return get_item_objects_for_location_update(payload)
    else:
        return get_item_objects_for_provider_update(payload)


def get_item_objects_for_item_update(payload):
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
            print(p["time"])
            i["provider_details"]["time"] = p["time"]
        item_objects.extend(db_items)
    return item_objects
