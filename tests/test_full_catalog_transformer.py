import unittest
import json
import os
from unittest.mock import patch

from funcy import empty

from config import get_config_by_name
from transformers.full_catalog import transform_full_on_search_payload_into_default_lang_items, \
    transform_full_on_search_payload_into_final_items


class TestFullCatalog(unittest.TestCase):

    mock_translated_text = "translated_text"

    def is_empty(self, val: dict):
        return empty(val) or len(val.keys()) == 0

    def test_on_search_simple(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/simple_on_search.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_attributes(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_attributes.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_offers(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_offers.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(4, len(items))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(4, len(offers))

    def test_on_search_with_customisation_group(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_customisation_group.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(12, len(items))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('services.translation_service.get_translated_text')
    def test_on_search_simple_with_translation(self, mock_translation_service):
        mock_translation_service.return_value = self.mock_translated_text
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ["ENV"] = "dev"
        filepath = os.path.join(current_path, "resources/simple_on_search.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_final_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        lang_length = len(list(filter(lambda x: x != "", get_config_by_name("LANGUAGE_LIST"))))+1
        self.assertEqual(1*lang_length, len(items))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_empty_locations_present(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_empty_locations_present.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(12, len(items))
        self.assertEqual(4, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_incorrect_parent_id(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_incorrect_parent_id.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_radius_more_than_5_km(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_radius_more_than_5_km.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(7, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_invalid_geoshape(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_invalid_geoshape.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(7, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_incorrect_pincode(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_incorrect_pincode.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_price_greater_than_max(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_price_greater_than_max.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_empty_customisation_groups(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_empty_customisation_groups.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(12, len(items))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_no_tags(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_no_tags.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    def test_on_search_with_no_origin_tag(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_no_origin_tag.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

