Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_customer_api/issues/16

# F-CA14: Pin api-utils 1.0.0 and migrate Customer API lists off infinite-scroll

This is the **first** `mentorhub_customer_api` issue for the 1.0.0 wave. It owns
the `api-utils==1.0.0` pin bump. Profile PATCH / inbound write RBAC is
**F-CA15** (`SHIPPED_ISSUE.mentorhub_customer_api.profile_control.md`) and should follow
this issue.

## Summary

R074 removed `execute_infinite_scroll_query` from api_utils. This repo still
pins `api-utils==0.2.1` and nine local list services still call that helper,
pass a raw PyMongo collection from `MongoIO.get_collection`, and return
`{items, limit, has_more, next_cursor}`. Matching list routes still read
`after_id` / `limit` query params.

Bump to **1.0.0** in the same change as the list-contract migration — 1.0.0
will not import.

Prefer **shared GET factories** (`create_*_get_routes`) plus a thin subclass
for collections that 1.0.0 already serves. Keep a local `execute_list_query`
implementation only for Customer-owned collections that are not in api_utils.

## Audit hits (still current)

### Direct `execute_infinite_scroll_query` import + call

| File | List method | 1.0.0 path |
|------|-------------|------------|
| `src/services/card_service.py` | `get_cards` | local `execute_list_query` (no shared Card service) |
| `src/services/customer_service.py` | `get_customers` | local `execute_list_query` (Customer **controls** Customer) |
| `src/services/dashboard_service.py` | `get_dashboards` | local `execute_list_query` (no shared Dashboard service) |
| `src/services/event_service.py` | `get_events` | thin `EventService` subclass + `create_event_get_routes` |
| `src/services/journey_service.py` | `get_journeys` | thin `JourneyService` subclass + `create_journey_get_routes` (by-id only; drop the local cursor list if OpenAPI has no Journey list, otherwise keep a local list via `execute_list_query` — shared Journey has **no** list method) |
| `src/services/note_service.py` | `get_notes` | thin `NoteService` subclass + `create_note_get_routes` (requires `resource_id`) |
| `src/services/profile_service.py` | `get_profiles` | thin `ProfileService` subclass + `create_profile_get_routes` |
| `src/services/rating_service.py` | `get_ratings` | local `execute_list_query` (Mentee **controls** Rating; no shared Rating service) |
| `src/services/subscription_service.py` | `get_subscriptions` | local `execute_list_query` (Payment; no shared Payment service) |

Each remaining local call site follows the same deprecated pattern:

```python
collection = mongo.get_collection(config.<COLLECTION>_COLLECTION_NAME)
result = execute_infinite_scroll_query(
    collection, name=name, after_id=after_id, limit=limit, ...
)
```

### Cursor query params (`after_id`) on list routes

`src/routes/card_routes.py`, `customer_routes.py`, `dashboard_routes.py`,
`event_routes.py`, `journey_routes.py`, `note_routes.py`, `profile_routes.py`,
`rating_routes.py`, `subscription_routes.py` — each `GET` list handler reads
`after_id` / `limit` / `sort_by` / `order` from `request.args` and returns the
`{items, has_more, next_cursor}` envelope.

### Cursor response envelope (`has_more`, `next_cursor`)

Same nine services and routes plus `docs/openapi.yaml`. Unit/route tests assert
the envelope; E2E tests
`test/e2e/test_{card,customer,dashboard,event,journey,note,profile,rating,subscription}.py`
require `has_more` / `next_cursor` keys.

## Pin (this issue owns the bump)

- Set `api-utils==1.0.0` in `Pipfile` / `Pipfile.lock` (currently `==0.2.1`).
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
| Mongo I/O | `get_collection` + `execute_infinite_scroll_query` | Shared GET factory **or** `execute_list_query(collection_name, match=, sort_by=, offset=, size=)` |

### Shared GET factories (preferred where they exist)

```python
from api_utils.routes.shared_get_routes import create_profile_get_routes
from src.services.profile_service import ProfileService

def create_profile_routes():
    bp = create_profile_get_routes(ProfileService)
    # POST/PATCH added in F-CA15
    return bp
```

```python
from api_utils.services import ProfileService as SharedProfileService

class ProfileService(SharedProfileService):
    """Customer consume + create via inherit; PATCH lands in F-CA15."""
```

Same thin-subclass + factory pattern for Event. Note list requires `resource_id`.
Journey factory is **by-id only** (`GET /<journey_id>`); there is no shared
Journey list.

### Local `execute_list_query` (Customer, Card, Dashboard, Rating, Subscription)

Do **not** call `mongo.get_collection(...)` for lists:

```python
from api_utils.flask_utils.list_request import parse_list_request
from api_utils.mongo_utils import (
    build_match_filter,
    execute_list_query,
)

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

Declare a `*_LIST_FILTERS` / `*_LIST_ORDER` next to each local service (name
contains is the existing filter; keep current allowed sort fields).

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
- List endpoints use offset/size headers and return a plain JSON array.
- OpenAPI and tests match the new contract.
- `pipenv run test`, `pipenv run lint`, `pipenv run build` pass.
- `pipenv run container`, `pipenv run api`, `pipenv run e2e` pass for every
  migrated list.

## What NOT to do

- Do not keep a local copy of `execute_infinite_scroll_query`.
- Do not continue passing raw collections from `MongoIO.get_collection` into
  list helpers — `execute_list_query` takes a collection **name**.
- Do not add Profile PATCH in this issue (F-CA15).
- Do not change non-list CRUD routes except where a shared GET factory
  replaces the list handler.
