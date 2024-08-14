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
    mock_flagged_items = []

    def is_empty(self, val: dict):
        return empty(val) or len(val.keys()) == 0

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_simple(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/simple_on_search.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_attributes(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_attributes.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_offers(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_offers.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(4, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(4, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_customisation_group(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_customisation_group.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))
        # Verify that the document retrieval was successful
        self.assertEqual(12, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    @patch('services.translation_service.get_translated_text')
    def test_on_search_simple_with_timing_on_search(self, mock_translation_service, mock_flagged_items_fn):
        mock_translation_service.return_value = self.mock_translated_text
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ["ENV"] = "dev"
        filepath = os.path.join(current_path, "resources/timing_on_search.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_final_items(json_payload)
            print(locations)

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    @patch('services.translation_service.get_translated_text')
    def test_on_search_simple_with_timing_on_search_with_multiple_per_day(self, mock_translation_service,
                                                                          mock_flagged_items_fn):
        mock_translation_service.return_value = self.mock_translated_text
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ["ENV"] = "dev"
        filepath = os.path.join(current_path, "resources/timing_on_search_with_multiple_timing_per_day.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_final_items(json_payload)
            print(locations)

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    @patch('services.translation_service.get_translated_text')
    def test_on_search_simple_with_timing_on_search_with_range_for_day(self, mock_translation_service,
                                                                       mock_flagged_items_fn):
        mock_translation_service.return_value = self.mock_translated_text
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ["ENV"] = "dev"
        filepath = os.path.join(current_path, "resources/timing_on_search_with_multiple_timing_for_range.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_final_items(json_payload)
            print(items)

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    @patch('services.translation_service.get_translated_text')
    def test_on_search_simple_with_translation(self, mock_translation_service, mock_flagged_items_fn):
        mock_translation_service.return_value = self.mock_translated_text
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.environ["ENV"] = "dev"
        filepath = os.path.join(current_path, "resources/simple_on_search.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_final_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        lang_length = len(list(filter(lambda x: x != "", get_config_by_name("LANGUAGE_LIST")))) + 1
        self.assertEqual(1, len(locations))
        self.assertEqual(1 * lang_length, len(items))
        self.assertEqual(0, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_empty_locations_present(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_empty_locations_present.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(12, len(items))
        self.assertEqual(2, len(locations))
        self.assertEqual(4, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_incorrect_parent_id(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_incorrect_parent_id.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_radius_more_than_5_km(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_radius_more_than_5_km.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(7, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_invalid_geoshape(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_invalid_geoshape.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(7, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_incorrect_pincode(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_incorrect_pincode.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_price_greater_than_max(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_price_greater_than_max.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_empty_customisation_groups(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_empty_customisation_groups.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(12, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_no_tags(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_no_tags.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))

    @patch('utils.elasticsearch_utils.get_all_manually_flagged_items_for_provider')
    def test_on_search_with_no_origin_tag(self, mock_flagged_items_fn):
        mock_flagged_items_fn.return_value = self.mock_flagged_items
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_no_origin_tag.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items, offers, locations = transform_full_on_search_payload_into_default_lang_items(json_payload)
            flagged_items = list(filter(lambda x: x["item_flag"], items))

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(1, len(locations))
        self.assertEqual(1, len(flagged_items))
        self.assertEqual(0, len(offers))
