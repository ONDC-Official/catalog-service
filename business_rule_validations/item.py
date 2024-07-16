from funcy import get_in
from shapely.geometry import shape

from business_rule_validations.city_to_pin_code_mappings import get_city_to_pin_codes_mapping


def validate_location_mapping(item):
    if len(item["location_details"]) != 0 or item["type"] == "customization":
        return None
    return {
        "code": "91027"
    }


def validate_circle_radius_if_present(item):
    radius = get_in(item, ["location_details", "radius"])
    if radius and (radius < 0 or radius > 5):
        return {
            "code": "90032"
        }
    else:
        return None


def validate_geoshape(item):
    geo_json = get_in(item, ["location_details", "polygons"])
    try:
        if geo_json is None:
            return None
        geom = shape(geo_json)

        if geom.is_valid:
            return None
        else:
            item["location_details"].pop("polygons")
            return {
                "code": "90032",
            }
    except Exception as e:
        item["location_details"].pop("polygons")
        return {
            "code": "90032"
        }


def validate_parent_item_id(item):
    parent_item_id = get_in(item, ["item_details", "parent_item_id"])
    if parent_item_id is not None and len(item["variant_group"]) == 0:
        return {
            "code": "91016"
        }
    else:
        return None


def validate_city_code_with_pin_code_in_locations(item):
    city_code = get_in(item, ["context", "city"])
    area_code = get_in(item, ["location_details", "address", "area_code"])

    city_pin_codes = get_city_to_pin_codes_mapping().get(city_code.split(":")[-1], [])

    if area_code and area_code not in city_pin_codes:
        return {
            "code": "90027"
        }
    else:
        return None


def validate_price_value_and_maximum_value(item):
    price = get_in(item, ["item_details", "price"])
    price_value = get_in(price, ["value"])
    max_price_value = get_in(price, ["maximum_value"])

    if max_price_value and float(price_value) > float(max_price_value):
        return {
            "code": "91001"
        }
    else:
        return None


def validate_parent_item_customisation_groups(item):
    customisation_groups = get_in(item, ["customisation_groups"], [])
    tags = get_in(item, ["item_details", "tags"], [])
    item_type = get_in(item, ["type"], "item")
    provider_id = get_in(item, ['provider_details', 'id'])
    customisation_group_id = None
    for t in tags:
        if t["code"] in ["custom_group", "parent"] and len(t.get("list", [])) > 0:
            customisation_group_id = f'{provider_id}_{t["list"][0]["value"]}'

    if customisation_group_id and len(customisation_groups) == 0 and item_type == "item":
        return {
            "code": "91029"
        }
    else:
        return None


def validate_item_tags(item):
    domain = get_in(item, ["context", "domain"])
    tags = get_in(item, ["item_details", "tags"])

    if domain != "ONDC:RET10" and tags is None:
        return {
            "code": "90020"
        }
    else:
        return None


def validate_item_tag_country_of_origin(item):
    domain = get_in(item, ["context", "domain"])
    tags = get_in(item, ["item_details", "tags"], [])
    origin_value = None
    for t in tags:
        if t["code"] == "origin" and len(t.get("list", [])) > 0:
            origin_value = t["list"][0]["value"]

    if domain != "ONDC:RET11" and origin_value is None:
        return {
            "code": "91012"
        }
    else:
        return None


def validate_item_level(item):
    validation_functions = [validate_location_mapping, validate_circle_radius_if_present, validate_geoshape,
                            validate_parent_item_id, validate_city_code_with_pin_code_in_locations,
                            validate_price_value_and_maximum_value, validate_parent_item_customisation_groups,
                            validate_item_tags, validate_item_tag_country_of_origin]
    item_error_tags = []
    for fn in validation_functions:
        resp = fn(item)
        if resp:
            item_error_tags.append(resp)

    return item_error_tags
