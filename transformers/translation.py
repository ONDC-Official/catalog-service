from services import translation_service as ts
from utils.instrumentation_utils import MeasureTime
from utils.parallel_processing_utils import io_bound_parallel_computation


@MeasureTime
def translate_items_into_target_language(items, target_lang):
    # io_bound_parallel_computation(lambda x: translate_an_item(x, target_lang), items)
    for x in items:
        translate_an_item(x, target_lang)
    return items


@MeasureTime
def translate_locations_into_target_language(locations, target_lang):
    # io_bound_parallel_computation(lambda x: translate_an_item(x, target_lang), items)
    for loc in locations:
        translate_a_location(loc, target_lang)
    return locations


def translate_an_item(i, target_lang):
    i["language"] = target_lang
    i["item_details"]["descriptor"] = translate_item_descriptor(i["item_details"]["descriptor"], target_lang)
    i["provider_details"]["descriptor"] = translate_item_descriptor(i["provider_details"]["descriptor"],
                                                                    target_lang)
    i["location_details"]["address"] = translate_location_address(i["location_details"].get("address", {}),
                                                                  target_lang)
    return i


def translate_a_location(i, target_lang):
    i["language"] = target_lang
    i["provider_details"]["descriptor"] = translate_item_descriptor(i["provider_details"]["descriptor"],
                                                                    target_lang)
    i["location_details"]["address"] = translate_location_address(i["location_details"].get("address", {}),
                                                                  target_lang)
    return i


def translate_item_descriptor(item_descriptor, target_lang):
    item_descriptor["name"] = ts.get_translated_text(item_descriptor["name"], target_lang=target_lang)
    if "short_desc" in item_descriptor:
        item_descriptor["short_desc"] = ts.get_translated_text(item_descriptor["short_desc"], target_lang=target_lang)
    if "long_desc" in item_descriptor:
        item_descriptor["long_desc"] = ts.get_translated_text(item_descriptor["long_desc"], target_lang=target_lang)
    return item_descriptor


def translate_provider_descriptor(provider_descriptor, target_lang):
    provider_descriptor["name"] = ts.get_translated_text(provider_descriptor["name"], target_lang=target_lang)
    if "short_desc" in provider_descriptor:
        provider_descriptor["short_desc"] = ts.get_translated_text(provider_descriptor["short_desc"],
                                                                   target_lang=target_lang)
    if "long_desc" in provider_descriptor:
        provider_descriptor["long_desc"] = ts.get_translated_text(provider_descriptor["long_desc"],
                                                                  target_lang=target_lang)
    return provider_descriptor


def translate_location_address(location_address, target_lang):
    if "city" in location_address:
        location_address["city"] = ts.get_translated_text(location_address["city"], target_lang=target_lang)
    if "locality" in location_address:
        location_address["locality"] = ts.get_translated_text(location_address["locality"], target_lang=target_lang)
    if "state" in location_address:
        location_address["state"] = ts.get_translated_text(location_address["state"], target_lang=target_lang)
    if "street" in location_address:
        location_address["street"] = ts.get_translated_text(location_address["street"], target_lang=target_lang)
    return location_address
