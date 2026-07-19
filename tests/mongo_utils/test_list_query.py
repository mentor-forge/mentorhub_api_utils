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
from api_utils.services.resource_service import (
    RESOURCE_LIST_FILTERS as SERVICE_RESOURCE_LIST_FILTERS,
)

# Local fixture for generic list_query behavior (name/description/status only).
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


class TestResourceMultiFieldFilters(unittest.TestCase):
    """Coverage for Resource SERVICE_RESOURCE_LIST_FILTERS (url, interests, etc.)."""

    def test_empty_and_omitted_produce_no_clauses(self):
        parsed = parse_filter_params({}, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(parsed, {})
        match = build_match_filter({}, parsed, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(match, {})

        blank_args = {
            "url": "",
            "interests": "",
            "technologies": "",
            "skill_level": "",
            "name": "",
        }
        parsed_blank = parse_filter_params(blank_args, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(parsed_blank, {})
        self.assertEqual(
            build_match_filter({}, parsed_blank, SERVICE_RESOURCE_LIST_FILTERS),
            {},
        )

    def test_whitespace_in_list_omitted(self):
        args = {
            "interests": "  ,  ",
            "technologies": "   ",
            "skill_level": ",",
        }
        parsed = parse_filter_params(args, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(parsed, {})
        self.assertNotIn("interests", parsed)
        self.assertNotIn("technologies", parsed)
        self.assertNotIn("skill_level", parsed)

    def test_url_contains_match(self):
        parsed = parse_filter_params(
            {"url": "example.com"}, SERVICE_RESOURCE_LIST_FILTERS
        )
        self.assertEqual(parsed["url"], "example.com")
        match = build_match_filter({}, parsed, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(match["url"]["$regex"], "example.com")
        self.assertEqual(match["url"]["$options"], "i")

    def test_in_list_match_clauses(self):
        args = {
            "interests": "python, data",
            "technologies": "flask",
            "skill_level": "beginner,intermediate",
        }
        parsed = parse_filter_params(args, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(parsed["interests"], ["python", "data"])
        self.assertEqual(parsed["technologies"], ["flask"])
        self.assertEqual(parsed["skill_level"], ["beginner", "intermediate"])

        match = build_match_filter({}, parsed, SERVICE_RESOURCE_LIST_FILTERS)
        self.assertEqual(match["interests"]["$in"], ["python", "data"])
        self.assertEqual(match["technologies"]["$in"], ["flask"])
        self.assertEqual(match["skill_level"]["$in"], ["beginner", "intermediate"])

    def test_combined_and_with_existing_filters(self):
        args = {
            "name": "alpha",
            "status": "active",
            "url": "docs",
            "interests": "career",
            "technologies": "react,vue",
            "skill_level": "advanced",
        }
        parsed = parse_filter_params(args, SERVICE_RESOURCE_LIST_FILTERS)
        match = build_match_filter({}, parsed, SERVICE_RESOURCE_LIST_FILTERS)

        self.assertEqual(match["name"]["$regex"], "alpha")
        self.assertEqual(match["name"]["$options"], "i")
        self.assertEqual(match["status"]["$in"], ["active"])
        self.assertEqual(match["url"]["$regex"], "docs")
        self.assertEqual(match["url"]["$options"], "i")
        self.assertEqual(match["interests"]["$in"], ["career"])
        self.assertEqual(match["technologies"]["$in"], ["react", "vue"])
        self.assertEqual(match["skill_level"]["$in"], ["advanced"])
        self.assertNotIn("$or", match)
        self.assertEqual(
            set(match.keys()),
            {
                "name",
                "status",
                "url",
                "interests",
                "technologies",
                "skill_level",
            },
        )


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
    def test_execute_list_query_calls_mongo_with_skip_limit(self, mock_get_mongo):
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
