"""
Outbound RBAC match helpers for shared GET/list operations.

Build Mongo match filters from the caller token (admin is unrestricted),
combine outbound scope with search filters without clobbering keys, and
evaluate fetched documents against the same match for get-by-id.
"""

from api_utils.config.config import Config
from api_utils.flask_utils.exceptions import HTTPNotFound
from api_utils.mongo_utils.list_query import and_match

# Match that yields zero documents when a scoped caller has no identity claims.
EMPTY_SCOPE_MATCH = {"_id": {"$in": []}}


def is_admin(token):
    """Return True when the token includes ROLE_ADMIN."""
    config = Config.get_instance()
    return config.ROLE_ADMIN in token.get("roles", [])


def build_outbound_match(token, clauses):
    """
    Build the outbound Mongo match for list/get visibility.

    Admin callers receive ``{}`` (unrestricted). Non-admin callers AND together
    the supplied clause dicts; empty or omitted clauses are skipped. Callers
    that require identity scope but have no identity claims should include
    :data:`EMPTY_SCOPE_MATCH` in ``clauses`` so results do not fall open.
    """
    if is_admin(token):
        return {}
    parts = [clause for clause in (clauses or []) if clause]
    if not parts:
        return {}
    return and_match(*parts)


def _field_value(document, field):
    """Read a dotted field path from a document."""
    value = document
    for segment in field.split("."):
        if not isinstance(value, dict) or segment not in value:
            return None
        value = value[segment]
    return value


def _matches_operator(document, field, operator, operand):
    """Evaluate a single Mongo comparison operator against a document field."""
    if operator == "$eq":
        return _field_value(document, field) == operand
    if operator == "$ne":
        return _field_value(document, field) != operand
    if operator == "$in":
        return _field_value(document, field) in operand
    if operator == "$exists":
        exists = _field_value(document, field) is not None
        return exists if operand else not exists
    return False


def _matches_field(document, field, condition):
    """Evaluate one field predicate against a document."""
    if isinstance(condition, dict) and any(key.startswith("$") for key in condition):
        for operator, operand in condition.items():
            if operator in ("$or", "$and"):
                continue
            if not _matches_operator(document, field, operator, operand):
                return False
        return True
    return _field_value(document, field) == condition


def matches_outbound(document, match):
    """
    Evaluate whether ``document`` satisfies the outbound ``match`` filter.

    Supports top-level field equality, ``$eq``, ``$ne``, ``$in``, ``$exists``,
    and nested ``$or`` / ``$and`` (including field-existence checks such as
    ``{"global": {"$exists": True}}``).
    """
    if not match:
        return True
    if document is None:
        return False

    if "$and" in match:
        return all(matches_outbound(document, clause) for clause in match["$and"])

    if "$or" in match:
        return any(matches_outbound(document, clause) for clause in match["$or"])

    for field, condition in match.items():
        if field.startswith("$"):
            continue
        if isinstance(condition, dict) and "$or" in condition:
            if not any(
                matches_outbound(document, {field: branch})
                for branch in condition["$or"]
            ):
                return False
            continue
        if isinstance(condition, dict) and "$and" in condition:
            if not all(
                matches_outbound(document, {field: branch})
                for branch in condition["$and"]
            ):
                return False
            continue
        if not _matches_field(document, field, condition):
            return False
    return True


def require_outbound(document, match, not_found_message="Not found"):
    """
    Return ``document`` when it satisfies ``match``; otherwise raise HTTPNotFound.

    Missing documents and outbound mismatches both surface as 404 so hidden ids
    are not leaked via 403.
    """
    if document is None or not matches_outbound(document, match or {}):
        raise HTTPNotFound(not_found_message)
    return document
