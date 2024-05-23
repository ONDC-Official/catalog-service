import unittest
import json
import os
from unittest.mock import patch
from funcy import empty

from transformers.incr_catalog import transform_incr_on_search_payload_into_final_items, \
    get_item_objects_for_item_update_for_default_language


class TestIncrCatalog(unittest.TestCase):

    current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    f = open(os.path.join(current_path, "resources/mock_search_documents_result.json"))
    mock_search_documents_value = json.load(f)
    mock_translated_text = "translated_text"

    def is_empty(self, val: dict):
        return empty(val) or len(val.keys()) == 0

    @patch('utils.elasticsearch_utils.search_documents')
    def test_incr_on_search_item_update_default_lang(self, mock_search_documents):
        mock_search_documents.return_value = self.mock_search_documents_value
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/incr_on_search_item_update.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items = get_item_objects_for_item_update_for_default_language(json_payload)

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))

    @patch('utils.elasticsearch_utils.search_documents')
    def test_incr_on_search_item_add_default_lang(self, mock_search_documents):
        mock_search_documents.return_value = self.mock_search_documents_value
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/incr_on_search_item_add.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items = get_item_objects_for_item_update_for_default_language(json_payload)

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))

    @patch('utils.elasticsearch_utils.search_documents')
    def test_incr_on_search_location_update(self, mock_search_documents):
        mock_search_documents.return_value = self.mock_search_documents_value
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/incr_on_search_location_update.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items = transform_incr_on_search_payload_into_final_items(json_payload)

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))

    @patch('utils.elasticsearch_utils.search_documents')
    def test_incr_on_search_provider_update(self, mock_search_documents):
        mock_search_documents.return_value = self.mock_search_documents_value
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/incr_on_search_provider_update.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items = transform_incr_on_search_payload_into_final_items(json_payload)

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))

    @patch('services.translation_service.get_translated_text')
    @patch('utils.elasticsearch_utils.search_documents')
    def test_incr_on_search_item_update(self, mock_search_documents, mock_translation_service):
        mock_search_documents.return_value = self.mock_search_documents_value
        mock_translation_service.return_value = self.mock_translated_text
        os.environ["ENV"] = "dev"
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/incr_on_search_item_update.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items = transform_incr_on_search_payload_into_final_items(json_payload)

        # Verify that the document retrieval was successful
        self.assertEqual(2, len(items))

    @patch('services.translation_service.get_translated_text')
    @patch('utils.elasticsearch_utils.search_documents')
    def test_incr_on_search_item_add(self, mock_search_documents, mock_translation_service):
        mock_search_documents.return_value = self.mock_search_documents_value
        mock_translation_service.return_value = self.mock_translated_text
        os.environ["ENV"] = "dev"
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/incr_on_search_item_add.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            items = transform_incr_on_search_payload_into_final_items(json_payload)

        # Verify that the document retrieval was successful
        self.assertEqual(2, len(items))
