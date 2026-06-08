"""
Unit tests for infinite scroll utilities.
"""
import unittest
from unittest.mock import MagicMock
from bson import ObjectId

from api_utils.mongo_utils.infinite_scroll import execute_infinite_scroll_query
from api_utils.flask_utils.exceptions import HTTPBadRequest


class TestExecuteInfiniteScrollQuery(unittest.TestCase):
    """Test execute_infinite_scroll_query."""

    def setUp(self):
        self.collection = MagicMock()
        self.allowed = ["name", "description", "status"]

    def _mock_cursor(self, items):
        cursor = MagicMock()
        cursor.sort.return_value = cursor
        cursor.limit.return_value = cursor
        cursor.__iter__.return_value = iter(items)
        self.collection.find.return_value = cursor
        return cursor

    def test_validation_limit_too_small(self):
        self.assertRaises(
            HTTPBadRequest,
            execute_infinite_scroll_query,
            self.collection,
            limit=0,
            allowed_sort_fields=self.allowed,
        )

    def test_validation_limit_too_large(self):
        self.assertRaises(
            HTTPBadRequest,
            execute_infinite_scroll_query,
            self.collection,
            limit=101,
            allowed_sort_fields=self.allowed,
        )

    def test_validation_invalid_sort_by(self):
        self.assertRaises(
            HTTPBadRequest,
            execute_infinite_scroll_query,
            self.collection,
            sort_by="invalid",
            allowed_sort_fields=self.allowed,
        )

    def test_validation_invalid_order(self):
        self.assertRaises(
            HTTPBadRequest,
            execute_infinite_scroll_query,
            self.collection,
            order="invalid",
            allowed_sort_fields=self.allowed,
        )

    def test_validation_invalid_after_id(self):
        self.assertRaises(
            HTTPBadRequest,
            execute_infinite_scroll_query,
            self.collection,
            after_id="not-an-object-id",
            allowed_sort_fields=self.allowed,
        )

    def test_first_page_no_more(self):
        items = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "a"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "b"},
        ]
        self._mock_cursor(items)

        result = execute_infinite_scroll_query(
            self.collection,
            limit=10,
            allowed_sort_fields=self.allowed,
        )

        self.assertEqual(len(result["items"]), 2)
        self.assertEqual(result["limit"], 10)
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["next_cursor"])
        self.collection.find.assert_called_once_with({})
        sort_call = self.collection.find.return_value.sort.call_args[0][0]
        self.assertEqual(sort_call, [("name", 1)])
        self.collection.find.return_value.limit.assert_called_once_with(11)

    def test_first_page_has_more(self):
        items = [
            {"_id": ObjectId(f"507f1f77bcf86cd7994390{i:02d}"), "name": f"item{i}"}
            for i in range(11)
        ]
        self._mock_cursor(items)

        result = execute_infinite_scroll_query(
            self.collection,
            limit=10,
            allowed_sort_fields=self.allowed,
        )

        self.assertEqual(len(result["items"]), 10)
        self.assertTrue(result["has_more"])
        self.assertEqual(result["next_cursor"], str(items[9]["_id"]))
        self.collection.find.return_value.limit.assert_called_once_with(11)

    def test_name_filter(self):
        items = [{"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "match"}]
        self._mock_cursor(items)

        execute_infinite_scroll_query(
            self.collection,
            name="match",
            allowed_sort_fields=self.allowed,
        )

        call_filter = self.collection.find.call_args[0][0]
        self.assertIn("name", call_filter)
        self.assertEqual(call_filter["name"]["$regex"], "match")
        self.assertEqual(call_filter["name"]["$options"], "i")

    def test_cursor_asc(self):
        items = [
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "b"},
            {"_id": ObjectId("507f1f77bcf86cd799439013"), "name": "c"},
        ]
        self._mock_cursor(items)

        execute_infinite_scroll_query(
            self.collection,
            after_id="507f1f77bcf86cd799439011",
            order="asc",
            allowed_sort_fields=self.allowed,
        )

        call_filter = self.collection.find.call_args[0][0]
        self.assertIn("_id", call_filter)
        self.assertIn("$gt", call_filter["_id"])

    def test_cursor_desc(self):
        items = [{"_id": ObjectId("507f1f77bcf86cd799439010"), "name": "a"}]
        self._mock_cursor(items)

        execute_infinite_scroll_query(
            self.collection,
            after_id="507f1f77bcf86cd799439011",
            order="desc",
            allowed_sort_fields=self.allowed,
        )

        call_filter = self.collection.find.call_args[0][0]
        self.assertIn("_id", call_filter)
        self.assertIn("$lt", call_filter["_id"])

    def test_sort_direction(self):
        self._mock_cursor([])

        execute_infinite_scroll_query(
            self.collection,
            sort_by="name",
            order="desc",
            allowed_sort_fields=self.allowed,
        )

        sort_call = self.collection.find.return_value.sort.call_args[0][0]
        self.assertEqual(sort_call, [("name", -1)])

    def test_default_allowed_sort_fields(self):
        self._mock_cursor([])

        execute_infinite_scroll_query(self.collection, sort_by="name")

        self.collection.find.assert_called_once()

    def test_empty_results(self):
        self._mock_cursor([])

        result = execute_infinite_scroll_query(
            self.collection,
            allowed_sort_fields=self.allowed,
        )

        self.assertEqual(result["items"], [])
        self.assertFalse(result["has_more"])
        self.assertIsNone(result["next_cursor"])
        self.assertEqual(result["limit"], 10)


if __name__ == "__main__":
    unittest.main()
