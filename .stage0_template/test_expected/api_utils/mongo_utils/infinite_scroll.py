"""
Infinite scroll (cursor-based pagination) utilities for MongoDB.

Provides reusable logic for list endpoints with server-side pagination,
sorting, and minimal name search.

Raises:
    HTTPBadRequest: If invalid parameters (limit, sort_by, order, after_id).
"""

from bson import ObjectId
from bson.errors import InvalidId

from api_utils.flask_utils.exceptions import HTTPBadRequest


def execute_infinite_scroll_query(
    collection,
    *,
    name=None,
    after_id=None,
    limit=10,
    sort_by="name",
    order="asc",
    allowed_sort_fields=None,
):
    """
    Execute a cursor-based infinite scroll query on a MongoDB collection.

    Validates parameters, builds filter and sort, runs find().sort().limit(limit+1),
    then returns {items, limit, has_more, next_cursor}. Uses _id for cursor.

    Args:
        collection: PyMongo Collection instance (e.g. from MongoIO.get_collection).
        name: Optional name filter; case-insensitive partial match via regex.
        after_id: Cursor – ID of last item from previous batch. Omit for first page.
        limit: Items per batch (1–100).
        sort_by: Field to sort by; must be in allowed_sort_fields.
        order: 'asc' or 'desc'.
        allowed_sort_fields: Sequence of allowed sort field names (e.g. for control:
            ['name', 'description', 'status', 'created.at_time', 'saved.at_time']).

    Returns:
        dict: {
            'items': list of documents,
            'limit': int,
            'has_more': bool,
            'next_cursor': str | None  # ID of last item, or None if no more
        }

    Raises:
        HTTPBadRequest: If limit, sort_by, order, or after_id are invalid.
    """
    allowed_sort_fields = allowed_sort_fields or ["name", "description"]

    if limit < 1:
        raise HTTPBadRequest("limit must be >= 1")
    if limit > 100:
        raise HTTPBadRequest("limit must be <= 100")
    if sort_by not in allowed_sort_fields:
        raise HTTPBadRequest(f"sort_by must be one of: {', '.join(allowed_sort_fields)}")
    if order not in ("asc", "desc"):
        raise HTTPBadRequest("order must be 'asc' or 'desc'")

    if after_id is not None:
        try:
            ObjectId(after_id)
        except (InvalidId, TypeError):
            raise HTTPBadRequest("after_id must be a valid MongoDB ObjectId")

    filter_query = {}
    if name:
        filter_query["name"] = {"$regex": name, "$options": "i"}
    if after_id is not None:
        direction = 1 if order == "asc" else -1
        op = "$gt" if order == "asc" else "$lt"
        filter_query["_id"] = {op: ObjectId(after_id)}

    sort_direction = 1 if order == "asc" else -1
    sort_spec = [(sort_by, sort_direction)]

    cursor = collection.find(filter_query).sort(sort_spec).limit(limit + 1)
    items = list(cursor)

    has_more = len(items) > limit
    if has_more:
        items = items[:limit]
        next_cursor = str(items[-1]["_id"])
    else:
        next_cursor = None

    return {
        "items": items,
        "limit": limit,
        "has_more": has_more,
        "next_cursor": next_cursor,
    }
