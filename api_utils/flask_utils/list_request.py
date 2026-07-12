"""
Flask request helpers for standardized Get List endpoints.
"""

from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_sort_by,
    parse_filter_params,
    parse_order_params,
    validate_pagination,
)


def parse_pagination_headers(request):
    """
    Read offset/size pagination from request headers.

    Returns:
        tuple: (offset, size)
    """
    offset = request.headers.get("offset", DEFAULT_OFFSET, type=int)
    size = request.headers.get("size", DEFAULT_SIZE, type=int)
    validate_pagination(offset, size)
    return offset, size


def parse_list_request(request, filter_spec, order_spec):
    """
    Parse pagination headers, filter query params, and order-by params.

    Returns:
        tuple: (offset, size, parsed_filters, sort_by)
            sort_by is a PyMongo sort list from build_sort_by.
    """
    offset, size = parse_pagination_headers(request)
    parsed_filters = parse_filter_params(request.args, filter_spec)
    field, order = parse_order_params(request.args, order_spec)
    sort_by = build_sort_by(field, order, order_spec)
    return offset, size, parsed_filters, sort_by
