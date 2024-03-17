from datetime import datetime

from funcy import get_in, omit


def enrich_provider_details_into_items(provider, item):
    provider_details = provider
    item["provider_details"] = omit(provider_details, ["locations", "items", "categories", "fulfillments"])
    return item


def enrich_location_details_into_items(locations, item):
    try:
        location = next(i for i in locations if i["id"] == get_in(item, ["item_details", "location_id"]))
    except:
        location = {}
    item["location_details"] = location
    return item


def enrich_category_details_into_items(categories, item):
    try:
        category = next(i for i in categories if i["id"] == get_in(item, ["item_details", "category_id"]))
    except:
        category = {}
    item["category_details"] = category
    return item


def enrich_fulfillment_details_into_items(fulfillments, item):
    try:
        fulfillment = next(i for i in fulfillments if i["id"] == get_in(item, ["item_details", "fulfillment_id"]))
    except:
        fulfillment = {}
    item["fulfillment_details"] = fulfillment
    return item


def enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, item):
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


def enrich_unique_id_in_item(item):
    item["local_id"] = item['item_details']['id']
    item["id"] = f"{item['bpp_details']['bpp_id']}_{item['provider_details']['id']}_{item['item_details']['id']}"
    return item


def flatten_item_attributes(item):
    tags = item["item_details"]["tags"]
    attr_list = []
    attr_dict = {}
    for t in tags:
        if t["code"] == "attribute":
            attr_list = t["list"]

    for a in attr_list:
        attr_dict[a["code"]] = a["value"]

    item["attributes"] = attr_dict
    return item


def enrich_item_type(item):
    item_details = item["item_details"]
    tags = item_details["tags"]
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
    for t in provider_details["tags"]:
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


def flatten_on_search_payload_to_provider_map(payload):
    provider_map = {}
    context = get_in(payload, ["context"])
    catalog = get_in(payload, ["message", "catalog"], {})

    bpp_id = get_in(context, ["bpp_id"])
    if bpp_id:
        bpp_descriptor = get_in(catalog, ["bpp/descriptor"])
        bpp_fulfillments = get_in(catalog, ["bpp/fulfillments"])
        bpp_providers = get_in(catalog, ["bpp/providers"])

        for p in bpp_providers:
            provider_locations = p.get("locations", [])
            provider_categories = p.get("categories", [])
            provider_items = p.get("items", [])
            provider_items = [{"item_details": i} for i in provider_items]
            [enrich_provider_details_into_items(p, i) for i in provider_items]
            [enrich_location_details_into_items(provider_locations, i) for i in provider_items]
            [enrich_fulfillment_details_into_items(bpp_fulfillments, i) for i in provider_items]
            [enrich_context_bpp_id_and_descriptor_into_items(context, bpp_id, bpp_descriptor, i)
             for i in provider_items]
            [cast_price_and_rating_to_float(i) for i in provider_items]
            [flatten_item_attributes(i) for i in provider_items]
            [enrich_item_type(i) for i in provider_items]
            [enrich_created_at_timestamp_in_item(i) for i in provider_items]
            [enrich_unique_id_in_item(i) for i in provider_items]
            provider_serviceabilities = get_provider_serviceabilities(p)

            provider_value = {
                "items": provider_items,
                "categories": provider_categories,
                "serviceabilities": provider_serviceabilities
            }
            provider_map[get_in(p, ["id"])] = provider_value

    return provider_map
