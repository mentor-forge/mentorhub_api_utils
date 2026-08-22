# Migrate Discovery API list endpoints off infinite-scroll cursors

> **Cross-repo issue artifact.** Paste-ready description for follow-on planning
> in **`mentorhub_discovery_api`**. Not part of the current `PENDING.*`
> orchestration chain in `mentorhub_api_utils` and must not be executed from
> that folder.
> **Blocked on**: `mentorhub_api_utils` list-query utilities shipped
> (`api-utils>=0.4.0`; pin **`==0.7.0`** — current published). R074 cannot
> delete `execute_infinite_scroll_query` until this repo has zero imports.

## Summary

R074 (`audit_and_remove_infinite_scroll`) found this repo still on the
deprecated cursor contract. Two local list services import
`execute_infinite_scroll_query`, pass a raw PyMongo collection from
`MongoIO.get_collection`, and return `{items, limit, has_more, next_cursor}`.
Matching list routes still read `after_id` / `limit` query params.

`Pipfile` currently pins `api-utils==0.5.2` (already has `list_query`). Bump
to `0.7.0`, switch Customer and Profile lists to the Standardized Get List
pattern used by `mentorhub_mentee_api` (`parse_list_request` +
`execute_list_query`), then delete all infinite-scroll imports so api_utils
can remove the module.

## Audit hits (R074, 2026-08-22)

### Direct `execute_infinite_scroll_query` import + call

| File | Import | Call | List method |
|------|--------|------|-------------|
| `src/services/customer_service.py` | L14 | L96 | `get_customers` |
| `src/services/profile_service.py` | L14 | L96 | `get_profiles` |

Each call site follows the same deprecated pattern:

```python
collection = mongo.get_collection(config.<COLLECTION>_COLLECTION_NAME)
result = execute_infinite_scroll_query(
    collection, name=name, after_id=after_id, limit=limit, ...
)
```

### Cursor query params (`after_id`) on list routes

- `src/routes/customer_routes.py` — `GET /api/customer` reads `after_id` (L58)
  and returns the `{items, has_more, next_cursor}` envelope.
- `src/routes/profile_routes.py` — `GET /api/profile` same contract (L58).

### Cursor response envelope (`has_more`, `next_cursor`)

Same two services and routes plus `docs/openapi.yaml` (Customer and Profile
list operations). Unit tests
`test/services/test_{customer,profile}_service.py` and route tests
`test/routes/test_{customer,profile}_routes.py` assert the envelope. E2E
`test/e2e/test_{customer,profile}.py` require `has_more` / `next_cursor` keys.

## Scope

### Dependency bump

- Pin `api-utils` to **`==0.7.0`** in `Pipfile` / `Pipfile.lock`.
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed).
- Do **not** use bare `pipenv install`.

`0.7.0` still exports `execute_infinite_scroll_query` (deprecated). After this
issue ships, api_utils R074 can delete the symbol in a patch (`0.7.1`).

### Replace list contract (Customer + Profile lists)

| Layer | Before (cursor) | After (Get List) |
|-------|-----------------|------------------|
| Pagination | Query `after_id`, `limit` | Headers `offset` (default `0`), `size` (default `20`, max `100`) |
| Response | `{items, limit, has_more, next_cursor}` | Plain JSON **array** |
| Name filter | Query `name` → regex inside infinite scroll | `filter_spec` `contains` on `name` via `parse_list_request` |
| Order | Query `sort_by` / `order` + `ALLOWED_SORT_FIELDS` | Per-endpoint `order_spec` + `build_sort_by` |
| Mongo I/O | `get_collection` + `execute_infinite_scroll_query` | `execute_list_query(collection_name, match=, sort_by=, offset=, size=)` |

Reference implementation: `mentorhub_mentee_api` `src/routes/resource_routes.py`
and `api_utils.services.resource_service` (`RESOURCE_LIST_FILTERS` /
`RESOURCE_LIST_ORDER` / `execute_list_query`).

Route sketch:

```python
from api_utils.flask_utils.list_request import parse_list_request

offset, size, filters, sort_by = parse_list_request(
    request, CUSTOMER_LIST_FILTERS, CUSTOMER_LIST_ORDER
)
items = CustomerService.get_customers(
    token, breadcrumb, offset, size, filters, sort_by
)
return jsonify(items), 200
```

Service sketch — **do not** call `mongo.get_collection(...)` for lists:

```python
from api_utils.mongo_utils import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_match_filter,
    execute_list_query,
)

match = build_match_filter({}, filters or {}, CUSTOMER_LIST_FILTERS)
return execute_list_query(
    config.CUSTOMER_COLLECTION_NAME,
    match=match,
    sort_by=sort_by,
    offset=offset,
    size=size,
)
```

Declare `CUSTOMER_LIST_FILTERS` / `CUSTOMER_LIST_ORDER` and
`PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER` next to each service (name
contains is the existing filter; keep current allowed sort fields
`name`, `description`).

### Docs and tests

- `docs/openapi.yaml` — replace `after_id` / `limit` / cursor envelope with
  `offset`/`size` headers and an array response (see mentee Path/Resource lists).
- Rewrite service/route unit tests that pass `after_id` or assert `has_more` /
  `next_cursor`.
- Rewrite E2E list tests to expect a JSON array.

### Confirmation

```bash
rg 'execute_infinite_scroll_query|after_id|has_more|next_cursor' --glob '*.py' --glob 'docs/openapi.yaml'
```

Zero hits required before R074 can proceed.

## Acceptance

- `Pipfile` pins `api-utils==0.7.0`.
- No `execute_infinite_scroll_query` import remains.
- Customer and Profile list endpoints use offset/size headers and return a
  plain JSON array.
- OpenAPI and tests match the new contract.
- `pipenv run test`, `pipenv run lint`, `pipenv run build` pass.
- `pipenv run container`, `pipenv run api`, `pipenv run e2e` pass for
  Customer and Profile lists.

## What NOT to do

- Do not keep a local copy of `execute_infinite_scroll_query`.
- Do not continue passing raw collections from `MongoIO.get_collection` into
  list helpers — `execute_list_query` takes a collection **name**.
- Do not change non-list CRUD routes in this issue.
