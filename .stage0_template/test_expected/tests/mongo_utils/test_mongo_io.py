"""
MongoIO Integration Tests

These tests require a running MongoDB instance accessible via the configured connection string.

To start the required MongoDB service for testing, run:
    stage0 up mongodb

All tests operate on a single test collection ('test_collection') and will create, modify, and delete documents within it. No production data or official config collections are used.
"""
import os
from copy import deepcopy
from datetime import datetime, timezone
import unittest
from unittest import TestLoader
from api_utils import Config, MongoIO
from pymongo import ASCENDING, DESCENDING
from unittest.mock import patch

class TestMongoIO(unittest.TestCase):
    
    def setUp(self):
        Config._instance = None
        # Set JWT_SECRET before initializing config to avoid validation error
        os.environ['JWT_SECRET'] = 'test-secret-for-mongo-tests'
        self.config = Config.get_instance()
        self.test_id = "eeee00000000000000009999"
        self.test_collection_name = "test_collection"
        self.test_document = {"name": "TestDoc", "sort_value": 1, "status": "active", "channels": [], "last_saved": {"fromIp": "", "byUser": "", "atTime": datetime(2025, 1, 1, 12, 34, 56), "correlationId": ""}}
        MongoIO._instance = None
        self.mongo_io = MongoIO.get_instance()
        self._setup_test_documents()

    def _setup_test_documents(self):
        # Clear any existing test data
        self.mongo_io.drop_collection(self.test_collection_name)
        # Insert test documents with different sort_value and name
        docs = [
            {"name": "Alpha", "sort_value": 1, "status": "active"},
            {"name": "Bravo", "sort_value": 2, "status": "active"},
            {"name": "Charlie", "sort_value": 3, "status": "inactive"},
            {"name": "Delta", "sort_value": 4, "status": "archived"},
            {"name": "Echo", "sort_value": 5, "status": "active"}
        ]
        for doc in docs:
            self.mongo_io.create_document(self.test_collection_name, doc)

    def tearDown(self):
        try:
            self.mongo_io.drop_collection(self.test_collection_name)
        except Exception:
            pass
        finally:
            self.mongo_io.disconnect()

    def test_singleton_behavior(self):
        mongo_io1 = MongoIO.get_instance()
        mongo_io2 = MongoIO.get_instance()
        self.assertIs(mongo_io1, mongo_io2, "MongoIO should be a singleton")
        self.mongo_io.disconnect()

    def test_CR_document(self):
        test_id = self.mongo_io.create_document(self.test_collection_name, self.test_document)
        id_str = str(test_id)
        document = self.mongo_io.get_document(self.test_collection_name, id_str)
        self.assertIsInstance(document, dict)
        self.assertEqual(document["name"], "TestDoc")

    def test_CRU_document(self):
        test_id = self.mongo_io.create_document(self.test_collection_name, self.test_document)
        id_str = str(test_id)
        test_update = {"status": "archived"}
        document = self.mongo_io.update_document(self.test_collection_name, id_str, set_data=test_update)
        self.assertIsInstance(document, dict)
        self.assertEqual(document["status"], "archived")

    def test_add_to_set_document(self):
        test_id = self.mongo_io.create_document(self.test_collection_name, self.test_document)
        id_str = str(test_id)
        test_add_to_set = {"channels": "channel1"}
        document = self.mongo_io.update_document(self.test_collection_name, id_str, add_to_set_data=test_add_to_set)
        self.assertIsInstance(document, dict)
        self.assertIn("channel1", document["channels"])

    def test_push_document(self):
        test_id = self.mongo_io.create_document(self.test_collection_name, self.test_document)
        id_str = str(test_id)
        push_data = {"channels": "channel1"}
        document = self.mongo_io.update_document(self.test_collection_name, id_str, push_data=push_data)
        self.assertIsInstance(document, dict)
        self.assertIn("channel1", document["channels"])

    def test_pull_from_document(self):
        test_id = self.mongo_io.create_document(self.test_collection_name, self.test_document)
        id_str = str(test_id)
        test_add_to_set = {"channels": "channel1"}
        self.mongo_io.update_document(self.test_collection_name, id_str, add_to_set_data=test_add_to_set)
        test_pull = {"channels": "channel1"}
        document = self.mongo_io.update_document(self.test_collection_name, id_str, pull_data=test_pull)
        self.assertIsInstance(document, dict)
        self.assertNotIn("channel1", document["channels"])

    def test_order_by_ASCENDING(self):
        order = [("sort_value", ASCENDING)]
        result = self.mongo_io.get_documents(self.test_collection_name, {}, {"name": 1, "sort_value": 1, "_id": 0}, order)
        self.assertEqual([doc["name"] for doc in result], ["Alpha", "Bravo", "Charlie", "Delta", "Echo"])

    def test_order_by_DESCENDING(self):
        order = [("sort_value", DESCENDING)]
        result = self.mongo_io.get_documents(self.test_collection_name, {}, {"name": 1, "sort_value": 1, "_id": 0}, order)
        self.assertEqual([doc["name"] for doc in result], ["Echo", "Delta", "Charlie", "Bravo", "Alpha"])

    def test_get_all_full_documents(self):
        result = self.mongo_io.get_documents(self.test_collection_name)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0]["name"], "Alpha")

    def test_get_some_full_documents(self):
        match = {"status": "archived"}
        result = self.mongo_io.get_documents(self.test_collection_name, match)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Delta")

    def test_get_all_partial_documents(self):
        project = {"_id": 0, "name": 1, "sort_value": 1}
        result = self.mongo_io.get_documents(self.test_collection_name, project=project)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 5)
        self.assertIn("name", result[0])
        self.assertIn("sort_value", result[0])
        self.assertNotIn("_id", result[0])

    def test_get_some_partial_documents(self):
        match = {"status": "inactive"}
        project = {"_id": 0, "name": 1, "sort_value": 1}
        result = self.mongo_io.get_documents(self.test_collection_name, match, project)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "Charlie")

    def test_upsert_document(self):
        match = {"name": "Foxtrot"}
        data = {"sort_value": 6, "status": "active"}
        document = self.mongo_io.upsert_document(self.test_collection_name, match, data)
        self.assertIsInstance(document, dict)
        self.assertEqual(document["name"], "Foxtrot")
        self.assertEqual(document["sort_value"], 6)
        # Test upsert with existing document
        data = {"sort_value": 7, "status": "inactive"}
        document = self.mongo_io.upsert_document(self.test_collection_name, match, data)
        self.assertIsInstance(document, dict)
        self.assertEqual(document["name"], "Foxtrot")
        self.assertEqual(document["sort_value"], 7)

if __name__ == '__main__':
    unittest.main()

