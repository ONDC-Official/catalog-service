import copy
from datetime import datetime

from funcy import get_in, omit


def enrich_provider_details(provider, item):
    provider_details = provider
    item["provider_details"] = omit(provider_details, ["locations", "items", "categories", "fulfillments", "offers"])
    return item


def enrich_location_details_into_item(locations, item):
    try:
        location = next(i for i in locations if i["id"] == get_in(item, ["item_details", "location_id"]))
        new_loc = copy.deepcopy(location)
        new_loc["local_id"] = new_loc["id"]
        new_loc["id"] = f"{item['provider_details']['id']}_{new_loc['local_id']}"
    except Exception as e:
        new_loc = {}
    item["location_details"] = new_loc
    return item


def enrich_location_details_into_offer(locations, offer, location_id):
    try:
        location = next(i for i in locations if i["id"] == location_id)
        new_loc = copy.deepcopy(location)
        new_loc["local_id"] = new_loc["id"]
        new_loc["id"] = f"{offer['provider_details']['id']}_{new_loc['local_id']}"
    except:
        new_loc = {}
    offer["location_details"] = new_loc
    return offer


def enrich_category_details_into_items(categories, item):
    try:
        category = next(i for i in categories if i["id"] == get_in(item, ["item_details", "category_id"]))
    except:
        category = {}
    item["category_details"] = category
    return item


def enrich_fulfillment_details(fulfillments, item):
    try:
        fulfillment = next(i for i in fulfillments if i["id"] == get_in(item, ["item_details", "fulfillment_id"]))
    except:
        fulfillment = {}
    item["fulfillment_details"] = fulfillment
    return item


def enrich_context_bpp_id_and_descriptor(context, bpp_id, bpp_descriptor, item):
    item["context"] = context
    item["bpp_details"] = bpp_descriptor
    item["bpp_details"]["bpp_id"] = bpp_id
    return item


def cast_price_and_rating_to_float(item_obj):
    item = get_in(item_obj, ["item_details"])
    if get_in(item, ["price", "value"]):
        item["price"]['value'] = float(get_in(item, ["price", "value"]))
    if get_in(item, ["rating"]):
        item["rating"] = float(get_in(item, ["rating"]))
    return item


def enrich_created_at_timestamp_in_item(item):
    item["created_at"] = datetime.utcnow()
    return item


def enrich_unique_id_into_item(item, provider_id):
    item["local_id"] = item['item_details']['id']
    item["id"] = f"{provider_id}_{item['item_details']['id']}"
    return item


def enrich_fulfillment_into_item(item, fulfillment):
    item["fulfillment"] = fulfillment
    return item


def enrich_unique_id_into_offer(offer, location_id):
    offer["local_id"] = offer['id']
    offer["id"] = f"{offer['provider_details']['id']}_{location_id}_{offer['id']}"
    return offer


def transform_key(key):
    updated_key = key.lower()
    key_mappings = {
        "gender_name": "gender",
        "brand_name": "brand",
    }
    if updated_key in key_mappings.keys():
        return key_mappings[updated_key]
    return updated_key


def flatten_item_attributes(item):
    tags = item["item_details"].get("tags", [])
    attr_list = []
    attr_final_list = []
    for t in tags:
        if t["code"] == "attribute":
            attr_list = t["list"]

    for a in attr_list:
        attr_final_list.append({"key": transform_key(a["code"]), "value": a["value"]})

    item["attribute_key_values"] = attr_final_list
    return item


def enrich_item_type(item):
    item_details = item["item_details"]
    tags = item_details.get("tags", [])
    item_type = "item"
    for t in tags:
        if t["code"] == "type":
            item_type = t["list"][0]["value"]

    item["type"] = item_type
    return item


def enrich_is_first_flag_for_items(items):
    variant_groups = set()
    for i in items:
        variant_group_local_id, variants = None, []
        categories = i["categories"]
        for c in categories:
            if i["item_details"].get("parent_item_id") == c["id"]:
                variant_group_local_id = c["id"]
                tags = c["tags"]
                for t in tags:
                    if t["code"] == "attr":
                        variants.append(t["list"])
        if len(variants) == 0:
            i["is_first"] = True
        else:
            i["is_first"] = variant_group_local_id not in variant_groups
        variant_groups.add(variant_group_local_id)
    return items


def get_provider_serviceabilities(provider_details):
    serviceabilities = dict()
    for t in provider_details.get("tags", []):
        if t["code"] == "serviceability":
            values = t["list"]
            serviceability = {}
            for v in values:
                if v["code"] == "location":
                    serviceability["location"] = v["value"]
                elif v["code"] == "type":
                    serviceability["type"] = v["value"]
                elif v["code"] == "unit":
                    serviceability["unit"] = v["value"]
                elif v["code"] == "val":
                    serviceability["val"] = v["value"]

            location_local_id = serviceability["location"]
            if location_local_id not in serviceabilities:
                serviceabilities[location_local_id] = [serviceability]
            # else:
            #     serviceabilities[location_local_id].append(serviceability)
    return serviceabilities


def flatten_full_on_search_payload_to_provider_map(payload):
    provider_map = {}
    context = get_in(payload, ["context"])
    catalog = get_in(payload, ["message", "catalog"], {})

    bpp_id = get_in(context, ["bpp_id"])
    if bpp_id:
        bpp_descriptor = get_in(catalog, ["bpp/descriptor"], {})
        bpp_fulfillments = get_in(catalog, ["bpp/fulfillments"], [])
        bpp_providers = get_in(catalog, ["bpp/providers"], [])

        for p in bpp_providers:
            p["local_id"] = p.get('id')
            p["id"] = f"{bpp_id}_{get_in(context, ['domain'])}_{p['local_id']}"
            p["fulfillments"] = p.get("fulfillments", [])
            # Enrich Items
            provider_items = p.get("items", [])
            provider_locations = p.get("locations", [])
            provider_categories = p.get("categories", [])
            provider_items = [{"item_details": i} for i in provider_items]
            [enrich_provider_details(p, i) for i in provider_items]
            [enrich_location_details_into_item(provider_locations, i) for i in provider_items]
            [enrich_fulfillment_details(bpp_fulfillments, i) for i in provider_items]
            [enrich_context_bpp_id_and_descriptor(context, bpp_id, bpp_descriptor, i) for i in provider_items]
            [cast_price_and_rating_to_float(i) for i in provider_items]
            [flatten_item_attributes(i) for i in provider_items]
            [enrich_item_type(i) for i in provider_items]
            [enrich_created_at_timestamp_in_item(i) for i in provider_items]
            [enrich_unique_id_into_item(i, p['id']) for i in provider_items]
            [enrich_fulfillment_into_item(i, p['fulfillments']) for i in provider_items]

            # Filter out the elements with location empty (for type as item)
            # TODO - log rejected items
            # provider_items = list(filter(lambda x: len(x["location_details"]) != 0 or x["type"] == "customization",
            #                              provider_items))

            # Enrich Offers
            provider_offers = p.get("offers", [])
            [enrich_provider_details(p, o) for o in provider_offers]
            [enrich_context_bpp_id_and_descriptor(context, bpp_id, bpp_descriptor, o) for o in provider_offers]

            location_offers = []
            for po in provider_offers:
                for loc_id in po["location_ids"]:
                    new_offer = copy.deepcopy(po)
                    enrich_location_details_into_offer(provider_locations, new_offer, loc_id)
                    enrich_unique_id_into_offer(new_offer, loc_id)
                    new_offer.pop("location_ids")
                    new_offer["item_local_ids"] = new_offer.pop("item_ids")
                    enrich_created_at_timestamp_in_item(new_offer)
                    location_offers.append(new_offer)

            provider_serviceabilities = get_provider_serviceabilities(p)
            provider_value = {
                "items": provider_items,
                "categories": provider_categories,
                "serviceabilities": provider_serviceabilities,
                "location_offers": location_offers,
                "provider_error_tags": [],
                "seller_error_tags": [],
            }
            provider_map[get_in(p, ["id"])] = provider_value

    return provider_map


def flatten_incr_on_search_payload_to_provider_map_for_items(payload):
    provider_map = {}
    context = get_in(payload, ["context"])
    catalog = get_in(payload, ["message", "catalog"], {})

    bpp_id = get_in(context, ["bpp_id"])
    if bpp_id:
        bpp_providers = get_in(catalog, ["bpp/providers"])

        for p in bpp_providers:
            p["local_id"] = p.get('id')
            p["id"] = f"{bpp_id}_{get_in(context, ['domain'])}_{p['local_id']}"
            provider_items = p.get("items", [])
            provider_items = [{"item_details": i} for i in provider_items]
            [cast_price_and_rating_to_float(i) for i in provider_items]
            [flatten_item_attributes(i) for i in provider_items]
            [enrich_item_type(i) for i in provider_items]
            [enrich_created_at_timestamp_in_item(i) for i in provider_items]
            [enrich_unique_id_into_item(i, p["id"]) for i in provider_items]

            provider_map[get_in(p, ["id"])] = provider_items

    return provider_map


def flatten_incr_on_search_payload_to_provider_map_for_offers(payload):
    provider_map = {}
    context = get_in(payload, ["context"])
    catalog = get_in(payload, ["message", "catalog"], {})

    bpp_id = get_in(context, ["bpp_id"])
    if bpp_id:
        bpp_descriptor = get_in(catalog, ["bpp/descriptor"], {})
        bpp_providers = get_in(catalog, ["bpp/providers"])

        for p in bpp_providers:
            p["local_id"] = p.get('id')
            p["id"] = f"{bpp_id}_{get_in(context, ['domain'])}_{p['local_id']}"

            # Enrich Offers
            provider_offers = p.get("offers", [])
            [enrich_provider_details(p, o) for o in provider_offers]
            [enrich_context_bpp_id_and_descriptor(context, bpp_id, bpp_descriptor, o) for o in provider_offers]

            location_offers = []
            for po in provider_offers:
                for loc_id in po["location_ids"]:
                    new_offer = copy.deepcopy(po)
                    new_offer["location_id"] = loc_id
                    enrich_unique_id_into_offer(new_offer, loc_id)
                    location_offers.append(new_offer)

            provider_map[get_in(p, ["id"])] = location_offers

    return provider_map


def flatten_incr_on_search_payload_to_provider_map_for_locations(payload):
    provider_map = {}
    context = get_in(payload, ["context"])
    catalog = get_in(payload, ["message", "catalog"], {})

    bpp_id = get_in(context, ["bpp_id"])
    if bpp_id:
        bpp_providers = get_in(catalog, ["bpp/providers"])

        for p in bpp_providers:
            p["local_id"] = p.get('id')
            p["id"] = f"{bpp_id}_{get_in(context, ['domain'])}_{p['local_id']}"
            provider_locations = p.get("locations", [])

            provider_map[get_in(p, ["id"])] = provider_locations

    return provider_map


def flatten_incr_on_search_payload_to_providers(payload):
    context = get_in(payload, ["context"])
    catalog = get_in(payload, ["message", "catalog"], {})

    bpp_id = get_in(context, ["bpp_id"])
    if bpp_id:
        bpp_providers = get_in(catalog, ["bpp/providers"])

        for p in bpp_providers:
            p["local_id"] = p.get('id')
            p["id"] = f"{bpp_id}_{get_in(context, ['domain'])}_{p['local_id']}"
        return bpp_providers

    return []
