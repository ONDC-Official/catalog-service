from services import translation_service as ts
from utils.instrumentation_utils import MeasureTime
from utils.parallel_processing_utils import io_bound_parallel_computation


@MeasureTime
def translate_items_into_target_language(items, target_lang):
    # io_bound_parallel_computation(lambda x: translate_an_item(x, target_lang), items)
    for x in items:
        translate_an_item(x, target_lang)


def translate_an_item(i, target_lang):
    i["language"] = target_lang
    i["item_details"]["descriptor"] = translate_item_descriptor(i["item_details"]["descriptor"], target_lang)
    i["provider_details"]["descriptor"] = translate_item_descriptor(i["provider_details"]["descriptor"],
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
