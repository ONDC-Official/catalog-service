import unittest
import json
import os
from funcy import empty

from transformers.first import flatten_on_search_payload_to_provider_map


class TestFirst(unittest.TestCase):

    def is_empty(self, val: dict):
        return empty(val) or len(val.keys()) == 0

    def test_on_search_simple(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/simple_on_search.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            provider_map = flatten_on_search_payload_to_provider_map(json_payload)
            items = provider_map["545016d9-ed19-4c02-833d-f4270436ffc0"]["items"]
            categories = provider_map["545016d9-ed19-4c02-833d-f4270436ffc0"]["categories"]
            serviceabilities = provider_map["545016d9-ed19-4c02-833d-f4270436ffc0"]["serviceabilities"]

        # Verify that the document retrieval was successful
        self.assertEqual(1, len(items))
        self.assertEqual(0, len(categories))
        self.assertEqual(1, len(serviceabilities))
        self.assertFalse(self.is_empty(items[0].get("item_details")))
        self.assertFalse(self.is_empty(items[0].get("bpp_details")))
        self.assertFalse(self.is_empty(items[0].get("context")))
        self.assertFalse(self.is_empty(items[0].get("provider_details")))
        self.assertFalse(self.is_empty(items[0].get("location_details")))
        self.assertFalse(self.is_empty(items[0].get("fulfillment_details")))
        self.assertTrue(self.is_empty(items[0].get("attributes")))

    def test_on_search_with_attributes(self):
        current_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(current_path, "resources/on_search_with_attributes.json")
        with open(filepath) as f:
            json_payload = json.load(f)
            provider_map = flatten_on_search_payload_to_provider_map(json_payload)
            items = provider_map["P1"]["items"]
            categories = provider_map["P1"]["categories"]
            serviceabilities = provider_map["P1"]["serviceabilities"]

        # Verify that the document retrieval was successful
        self.assertEqual(7, len(items))
        self.assertEqual(1, len(categories))
        self.assertEqual(1, len(serviceabilities))
        self.assertFalse(self.is_empty(items[0].get("item_details")))
        self.assertFalse(self.is_empty(items[0].get("bpp_details")))
        self.assertFalse(self.is_empty(items[0].get("context")))
        self.assertFalse(self.is_empty(items[0].get("provider_details")))
        self.assertFalse(self.is_empty(items[0].get("location_details")))
        self.assertTrue(self.is_empty(items[0].get("fulfillment_details")))
        self.assertFalse(self.is_empty(items[0].get("attributes")))
