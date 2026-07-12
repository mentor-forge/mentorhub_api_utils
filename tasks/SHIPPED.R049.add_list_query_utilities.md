# R049 – Add standardized Get List query utilities

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R048_add_mongoio_skip_limit`  
**Description**: Introduce shared pagination constants, validation, extensible query-parameter parsing (filters **and order-by**), and a MongoIO-backed paginated list executor to replace the cursor-based `execute_infinite_scroll_query` pattern.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/mongo_io.py` — R048 `skip`/`limit`
- `api_utils/mongo_utils/infinite_scroll.py` — legacy cursor pagination (to be deprecated in R053)
- `api_utils/services/resource_service.py` — partial precedent: `DEFAULT_OFFSET`, `DEFAULT_SIZE`, `MAX_SIZE`, `_validate_pagination`
- `../mentorhub_mentee_api/src/routes/resource_routes.py` — route reads `offset`/`size` from **request headers** (defaults `0`/`20`)
- `tests/mongo_utils/test_infinite_scroll.py` — reference for filter/sort validation tests

### Target contract (service + route layers)

| Concern | Convention |
|--------|------------|
| Pagination | Request headers `offset` (default `0`) and `size` (default `20`, max `100`) |
| Response body | Plain JSON **array** of documents (no `items`/`has_more`/`next_cursor` wrapper) |
| Text search | Query param on field → case-insensitive substring match (`contains`) |
| Enum filter | Query param with comma-separated values → MongoDB `$in` (`in_list`) |
| Scoped lists | Service supplies a base `match` (e.g. `resource_id`, RBAC scope); pagination and filters apply within that scope |
| Order by | Query params `sort_by` + `order` (`asc`/`desc`); per-endpoint `order_spec` declares allowed fields, defaults, and directions |
| MongoDB I/O | `MongoIO.get_documents(..., skip=offset, limit=size, sort_by=...)` via `list_query.execute_list_query` |

### Extensible filter spec (illustrative)

```python
RESOURCE_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "description": {"type": "contains", "field": "description"},
    "status": {"type": "in_list", "field": "status"},
}
```

Query examples: `?description=onboard&status=active,draft`

### Extensible order-by spec (illustrative)

Each list endpoint declares an **`order_spec`** that whitelists client-selectable sort fields and directions. Omitted query params use the spec default. Services with a fixed sort (e.g. mentee Path list) declare an `order_spec` with a single allowed field/direction so the interface stays consistent even when the client cannot meaningfully change sort.

```python
RESOURCE_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {
        "name": ("asc", "desc"),
        "description": ("asc", "desc"),
        "status": ("asc", "desc"),
        "created.at_time": ("asc", "desc"),
        "saved.at_time": ("asc", "desc"),
    },
}
```

Query examples: `?sort_by=created.at_time&order=desc` (with `offset`/`size` headers)

**Stable pagination**: `build_sort_by(...)` appends a tiebreaker on `_id` (same direction as primary sort) so offset paging is deterministic when the primary field has duplicate values.

**Validation**: Unknown `sort_by` or disallowed `order` for that field → `HTTPBadRequest` with a message listing permitted options from the spec.

## Goals

- Add `api_utils/mongo_utils/list_query.py` with:
  - `DEFAULT_OFFSET = 0`, `DEFAULT_SIZE = 20`, `MAX_SIZE = 100`
  - `validate_pagination(offset, size)` → raises `HTTPBadRequest` on invalid values
  - `parse_filter_params(args, filter_spec)` — build filter dict from Flask/Werkzeug `request.args` (or any mapping)
  - `build_match_filter(base_match, parsed_filters, filter_spec)` — merge base scope + filter clauses into a MongoDB `match` dict
  - **Order-by interface**:
    - `parse_order_params(args, order_spec)` — read `sort_by` and `order` query params; apply `order_spec["default"]` when omitted
    - `validate_order(field, order, order_spec)` — field must be in `order_spec["allowed"]`; `order` must be listed for that field
    - `build_sort_by(field, order, order_spec)` — return PyMongo sort list `[(field, ASCENDING|DESCENDING), ("_id", ...)]` with stable `_id` tiebreaker
    - Document `order_spec` shape: `{"default": {"field": str, "order": "asc"|"desc"}, "allowed": {field: ("asc", "desc", ...)}}`
  - `execute_list_query(collection_name, *, match, sort_by, offset, size, project=None)` — calls `MongoIO.get_documents` with `skip=offset`, `limit=size`
- Add `api_utils/flask_utils/list_request.py` with:
  - `parse_pagination_headers(request)` → `(offset, size)` using header defaults
  - `parse_list_request(request, filter_spec, order_spec)` → `(offset, size, parsed_filters, sort_by)` — `sort_by` is the PyMongo sort list from `build_sort_by`
- Export new symbols from `api_utils/mongo_utils/__init__.py` and `api_utils/__init__.py` (or `flask_utils` package `__init__` if one exists).
- Unit tests in `tests/mongo_utils/test_list_query.py` and `tests/flask_utils/test_list_request.py` covering pagination validation, `contains`/`in_list` filter building, **order-by parsing/validation/defaults/tiebreaker**, and paginated execution (mock `MongoIO`).

## Testing Expectations

- `pipenv run test tests/mongo_utils/test_list_query.py`
- `pipenv run test tests/flask_utils/test_list_request.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/mongo_utils/list_query.py`
- `api_utils/flask_utils/list_request.py`
- `api_utils/mongo_utils/__init__.py` — export list-query symbols
- `api_utils/__init__.py` — re-export public list-query symbols (if top-level export is the package convention)
- `tests/mongo_utils/test_list_query.py`
- `tests/flask_utils/test_list_request.py`

The agent must not update files outside this list.

## Execution Notes

- Added `list_query.py` and `list_request.py` with pagination, filter, and order-by helpers.
- Fixed circular import by importing `MongoIO` from `mongo_io` directly in `list_query`.
- `pipenv run test`: 173 passed, 6 deselected.
