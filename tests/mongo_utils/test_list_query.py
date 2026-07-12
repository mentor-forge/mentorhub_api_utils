"""
Unit tests for list query utilities.
"""

import unittest
from unittest.mock import MagicMock, patch

from pymongo import ASCENDING, DESCENDING

from api_utils.flask_utils.exceptions import HTTPBadRequest
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    MAX_SIZE,
    build_match_filter,
    build_sort_by,
    execute_list_query,
    parse_filter_params,
    parse_order_params,
    validate_order,
    validate_pagination,
)

RESOURCE_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "description": {"type": "contains", "field": "description"},
    "status": {"type": "in_list", "field": "status"},
}

RESOURCE_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {
        "name": ("asc", "desc"),
        "created.at_time": ("asc", "desc"),
    },
}


class TestValidatePagination(unittest.TestCase):
    def test_defaults_are_valid(self):
        validate_pagination(DEFAULT_OFFSET, DEFAULT_SIZE)

    def test_invalid_offset(self):
        with self.assertRaises(HTTPBadRequest):
            validate_pagination(-1, DEFAULT_SIZE)

    def test_invalid_size(self):
        with self.assertRaises(HTTPBadRequest):
            validate_pagination(0, 0)
        with self.assertRaises(HTTPBadRequest):
            validate_pagination(0, MAX_SIZE + 1)


class TestFilterParsing(unittest.TestCase):
    def test_parse_contains_and_in_list(self):
        args = {"name": "alpha", "status": "active,archived"}
        parsed = parse_filter_params(args, RESOURCE_LIST_FILTERS)
        self.assertEqual(parsed["name"], "alpha")
        self.assertEqual(parsed["status"], ["active", "archived"])

    def test_build_match_filter(self):
        parsed = {"name": "alpha", "status": ["active"]}
        match = build_match_filter({}, parsed, RESOURCE_LIST_FILTERS)
        self.assertEqual(match["name"]["$regex"], "alpha")
        self.assertEqual(match["status"]["$in"], ["active"])


class TestOrderBy(unittest.TestCase):
    def test_parse_order_defaults(self):
        field, order = parse_order_params({}, RESOURCE_LIST_ORDER)
        self.assertEqual(field, "name")
        self.assertEqual(order, "asc")

    def test_parse_order_custom(self):
        field, order = parse_order_params(
            {"sort_by": "created.at_time", "order": "desc"},
            RESOURCE_LIST_ORDER,
        )
        self.assertEqual(field, "created.at_time")
        self.assertEqual(order, "desc")

    def test_invalid_sort_by(self):
        with self.assertRaises(HTTPBadRequest):
            validate_order("invalid", "asc", RESOURCE_LIST_ORDER)

    def test_invalid_order_direction(self):
        with self.assertRaises(HTTPBadRequest):
            validate_order("name", "sideways", RESOURCE_LIST_ORDER)

    def test_build_sort_by_includes_id_tiebreaker(self):
        sort_by = build_sort_by("name", "desc", RESOURCE_LIST_ORDER)
        self.assertEqual(sort_by, [("name", DESCENDING), ("_id", DESCENDING)])


class TestExecuteListQuery(unittest.TestCase):
    @patch("api_utils.mongo_utils.list_query.MongoIO.get_instance")
    def test_execute_list_query_calls_mongo_with_skip_limit(
        self, mock_get_mongo
    ):
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [{"_id": "1"}]
        mock_get_mongo.return_value = mock_mongo

        result = execute_list_query(
            "Resource",
            match={"status": "active"},
            sort_by=[("name", ASCENDING), ("_id", ASCENDING)],
            offset=10,
            size=5,
        )

        self.assertEqual(result, [{"_id": "1"}])
        mock_mongo.get_documents.assert_called_once_with(
            "Resource",
            match={"status": "active"},
            project=None,
            sort_by=[("name", ASCENDING), ("_id", ASCENDING)],
            skip=10,
            limit=5,
        )


if __name__ == "__main__":
    unittest.main()
