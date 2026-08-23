Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_discovery_api/issues/5

# F-DA02: Pin api-utils 1.0.0 and migrate Discovery API lists off infinite-scroll

This is the **first** `mentorhub_discovery_api` issue for the 1.0.0 wave. It owns
the `api-utils==1.0.0` pin bump. Notification dismiss / control is **F-DA03**
(`SHIPPED_ISSUE.mentorhub_discovery_api.notification_control.md`) and should follow
this issue.

## Summary

R074 removed `execute_infinite_scroll_query` from api_utils. This repo still
pins `api-utils==0.5.2` and two local list services still call that helper,
pass a raw PyMongo collection from `MongoIO.get_collection`, and return
`{items, limit, has_more, next_cursor}`. Matching list routes still read
`after_id` / `limit` query params.

Bump to **1.0.0** in the same change as the list-contract migration — 1.0.0
will not import.

Discovery **consumes** Profile (shared GET factory exists) and has a local
Customer list (no shared `CustomerService`). Prefer the shared Profile factory
over rewriting Profile as another local `execute_list_query`.

## Audit hits (still current)

### Direct `execute_infinite_scroll_query` import + call

| File | List method | 1.0.0 path |
|------|-------------|------------|
| `src/services/customer_service.py` | `get_customers` | local `execute_list_query` (no shared Customer service) |
| `src/services/profile_service.py` | `get_profiles` | thin `ProfileService` subclass + `create_profile_get_routes` |

Each remaining local call site follows the same deprecated pattern:

```python
collection = mongo.get_collection(config.<COLLECTION>_COLLECTION_NAME)
result = execute_infinite_scroll_query(
    collection, name=name, after_id=after_id, limit=limit, ...
)
```

### Cursor query params (`after_id`) on list routes

- `src/routes/customer_routes.py` — `GET /api/customer` reads `after_id`
  and returns the `{items, has_more, next_cursor}` envelope.
- `src/routes/profile_routes.py` — `GET /api/profile` same contract.

### Cursor response envelope (`has_more`, `next_cursor`)

Same two services and routes plus `docs/openapi.yaml` (Customer and Profile
list operations). Unit tests
`test/services/test_{customer,profile}_service.py` and route tests
`test/routes/test_{customer,profile}_routes.py` assert the envelope. E2E
`test/e2e/test_{customer,profile}.py` require `has_more` / `next_cursor` keys.

## Pin (this issue owns the bump)

- Set `api-utils==1.0.0` in `Pipfile` / `Pipfile.lock` (currently `==0.5.2`).
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed).
- Do **not** use bare `pipenv install`.

`1.0.0` **does not** export `execute_infinite_scroll_query`. The pin bump and
list-contract migration must land together.

## Replace list contract

| Layer | Before (cursor) | After (Get List) |
|-------|-----------------|------------------|
| Pagination | Query `after_id`, `limit` | Headers `offset` (default `0`), `size` (default `20`, max `100`) |
| Response | `{items, limit, has_more, next_cursor}` | Plain JSON **array** |
| Name filter | Query `name` → regex inside infinite scroll | `filter_spec` `contains` on `name` via `parse_list_request` |
| Order | Query `sort_by` / `order` + `ALLOWED_SORT_FIELDS` | Per-endpoint `order_spec` + `build_sort_by` |
| Mongo I/O | `get_collection` + `execute_infinite_scroll_query` | Shared GET factory **or** `execute_list_query(collection_name, ...)` |

### Profile — shared GET factory

```python
from api_utils.services import ProfileService as SharedProfileService
from api_utils.routes.shared_get_routes import create_profile_get_routes

class ProfileService(SharedProfileService):
    """Discovery consumes Profile; no Profile PATCH here."""

def create_profile_routes():
    return create_profile_get_routes(ProfileService)
```

List GET body is a JSON array; pagination is `offset`/`size` request headers
only (no cursor, no `X-Pagination-*`).

### Customer — local `execute_list_query`

Do **not** call `mongo.get_collection(...)` for lists:

```python
from api_utils.flask_utils.list_request import parse_list_request
from api_utils.mongo_utils import build_match_filter, execute_list_query

offset, size, filters, sort_by = parse_list_request(
    request, CUSTOMER_LIST_FILTERS, CUSTOMER_LIST_ORDER
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

Declare `CUSTOMER_LIST_FILTERS` / `CUSTOMER_LIST_ORDER` next to the local
service (name contains is the existing filter; keep current allowed sort
fields `name`, `description`).

## Docs and tests

- `docs/openapi.yaml` — replace `after_id` / `limit` / cursor envelope with
  `offset`/`size` headers and an array response.
- Rewrite service/route unit tests that pass `after_id` or assert `has_more` /
  `next_cursor`.
- Rewrite E2E list tests to expect a JSON array.

## Confirmation

```bash
rg 'execute_infinite_scroll_query|after_id|has_more|next_cursor' --glob '*.py' --glob 'docs/openapi.yaml'
```

Zero hits required after the `api-utils==1.0.0` bump.

## Acceptance

- `Pipfile` pins `api-utils==1.0.0`.
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
- Do not add Notification dismiss in this issue (F-DA03).
- Do not add control mutations for collections Discovery does not control.
