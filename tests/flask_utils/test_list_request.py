"""
Unit tests for Flask list request helpers.
"""

import unittest
from unittest.mock import MagicMock

from api_utils.flask_utils.exceptions import HTTPBadRequest
from api_utils.flask_utils.list_request import (
    parse_list_request,
    parse_pagination_headers,
)

RESOURCE_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "status": {"type": "in_list", "field": "status"},
}

RESOURCE_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {"name": ("asc", "desc")},
}


def _make_request(headers=None, args=None):
    request = MagicMock()
    header_map = headers or {}

    def header_get(key, default=None, type=str):
        if key not in header_map:
            return default
        return type(header_map[key])

    request.headers.get = header_get
    request.args = args or {}
    return request


class TestListRequest(unittest.TestCase):
    def test_parse_pagination_headers_defaults(self):
        request = _make_request()
        offset, size = parse_pagination_headers(request)
        self.assertEqual(offset, 0)
        self.assertEqual(size, 20)

    def test_parse_pagination_headers_custom(self):
        request = _make_request(headers={"offset": "5", "size": "10"})
        offset, size = parse_pagination_headers(request)
        self.assertEqual(offset, 5)
        self.assertEqual(size, 10)

    def test_parse_list_request(self):
        request = _make_request(
            headers={"offset": "0", "size": "20"},
            args={"name": "alpha", "sort_by": "name", "order": "desc"},
        )
        offset, size, filters, sort_by = parse_list_request(
            request, RESOURCE_LIST_FILTERS, RESOURCE_LIST_ORDER
        )
        self.assertEqual(offset, 0)
        self.assertEqual(size, 20)
        self.assertEqual(filters["name"], "alpha")
        self.assertEqual(sort_by[0][0], "name")

    def test_parse_pagination_invalid_size(self):
        request = _make_request(headers={"size": "0"})
        with self.assertRaises(HTTPBadRequest):
            parse_pagination_headers(request)


if __name__ == "__main__":
    unittest.main()
