"""
Standardized Get List query utilities for MongoDB-backed list endpoints.

Provides pagination validation, extensible filter and order-by parsing,
and a MongoIO-backed paginated list executor.
"""

from pymongo import ASCENDING, DESCENDING

from api_utils.flask_utils.exceptions import HTTPBadRequest
from api_utils.mongo_utils.mongo_io import MongoIO

DEFAULT_OFFSET = 0
DEFAULT_SIZE = 20
MAX_SIZE = 100


def validate_pagination(offset, size):
    """Validate offset/size pagination parameters."""
    if offset < 0:
        raise HTTPBadRequest("offset must be >= 0")
    if size < 1:
        raise HTTPBadRequest("size must be >= 1")
    if size > MAX_SIZE:
        raise HTTPBadRequest(f"size must be <= {MAX_SIZE}")


def _get_arg(args, key):
    if hasattr(args, "get"):
        return args.get(key)
    return args.get(key) if key in args else None


def parse_filter_params(args, filter_spec):
    """
    Build a filter dict from request query parameters using filter_spec.

    filter_spec maps param names to {"type": "contains"|"in_list", "field": str}.
    """
    parsed = {}
    for param_name, spec in (filter_spec or {}).items():
        raw = _get_arg(args, param_name)
        if raw is None or raw == "":
            continue
        if spec["type"] == "contains":
            parsed[param_name] = raw
        elif spec["type"] == "in_list":
            values = [value.strip() for value in str(raw).split(",") if value.strip()]
            if values:
                parsed[param_name] = values
    return parsed


def build_match_filter(base_match, parsed_filters, filter_spec):
    """Merge base scope match with parsed filter clauses."""
    match = dict(base_match or {})
    for param_name, value in (parsed_filters or {}).items():
        spec = filter_spec.get(param_name)
        if spec is None:
            continue
        field = spec["field"]
        if spec["type"] == "contains":
            match[field] = {"$regex": value, "$options": "i"}
        elif spec["type"] == "in_list":
            match[field] = {"$in": list(value)}
    return match


def parse_order_params(args, order_spec):
    """
    Read sort_by and order query params; apply order_spec default when omitted.

    Returns:
        tuple: (field, order) where order is 'asc' or 'desc'.
    """
    default = order_spec["default"]
    field = _get_arg(args, "sort_by") or default["field"]
    order = (_get_arg(args, "order") or default["order"]).lower()
    validate_order(field, order, order_spec)
    return field, order


def validate_order(field, order, order_spec):
    """Validate sort field and direction against order_spec."""
    allowed = order_spec.get("allowed", {})
    if field not in allowed:
        permitted = ", ".join(sorted(allowed.keys()))
        raise HTTPBadRequest(f"sort_by must be one of: {permitted}")
    if order not in ("asc", "desc"):
        raise HTTPBadRequest("order must be 'asc' or 'desc'")
    permitted_orders = allowed[field]
    if order not in permitted_orders:
        permitted = ", ".join(permitted_orders)
        raise HTTPBadRequest(
            f"order for '{field}' must be one of: {permitted}"
        )


def build_sort_by(field, order, order_spec=None):
    """
    Return PyMongo sort list with stable _id tiebreaker.

    order_spec is optional when field/order are already validated.
    """
    if order_spec is not None:
        validate_order(field, order, order_spec)
    direction = ASCENDING if order == "asc" else DESCENDING
    return [(field, direction), ("_id", direction)]


def execute_list_query(
    collection_name,
    *,
    match=None,
    sort_by=None,
    offset=DEFAULT_OFFSET,
    size=DEFAULT_SIZE,
    project=None,
):
    """
    Execute a paginated list query via MongoIO.get_documents.

    Args:
        collection_name: MongoDB collection name.
        match: MongoDB match filter.
        sort_by: PyMongo sort list (from build_sort_by).
        offset: Zero-based skip count.
        size: Page size.
        project: Optional projection dict.

    Returns:
        list: Matching documents for the requested page.
    """
    validate_pagination(offset, size)
    mongo = MongoIO.get_instance()
    return mongo.get_documents(
        collection_name,
        match=match or {},
        project=project,
        sort_by=sort_by,
        skip=offset,
        limit=size,
    )
