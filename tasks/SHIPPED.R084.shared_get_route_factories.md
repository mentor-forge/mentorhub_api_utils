# R084 – Shared `create_*_get_routes` factories

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R083_flatten_get_resource_to_document`  
**Description**: Add Flask blueprint factories for every shared consume GET. Each factory takes the **local service subclass** (`service_cls`). List GETs return a JSON array with offset/size request pagination only.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md` — route factories return Blueprints; HTTP layer is token, breadcrumb, parse, call service, jsonify
- `README.md` — data-boundary contract (**routes import the local subclass**)
- `tasks/_PLANNING.md` — **Standardized Get List pattern**
- `tasks/_ORCHESTRATE.md`
- `api_utils/routes/config_routes.py` — factory pattern (`create_config_routes`)
- `api_utils/flask_utils/list_request.py` — `parse_list_request`
- `api_utils/flask_utils/route_wrapper.py` — `handle_route_exceptions`
- `api_utils/__init__.py` — current route exports
- `../mentorhub_mentee_api/src/routes/resource_routes.py` — copy-paste GET to harvest
- `../mentorhub_mentor_api/src/routes/resource_routes.py` — has extra `X-Pagination-*`; **do not** copy those headers
- Each `api_utils/services/*_service.py` GET/list method and its `*_LIST_FILTERS` / `*_LIST_ORDER` constants

### Contract

```python
def create_resource_get_routes(service_cls, *, name="resource_routes"):
    ...
```

- `service_cls` is **required**. Factories must not default to `api_utils.services.ResourceService` so domain APIs cannot accidentally bind the shared class.
- Domain APIs **include** GETs then add POST/PATCH on the same Blueprint:

```python
from api_utils.routes.shared_get_routes import create_resource_get_routes
from src.services.resource_service import ResourceService

def create_resource_routes():
    bp = create_resource_get_routes(ResourceService)
    @bp.route("", methods=["POST"])
    def create_resource():
        ...
    return bp
```

- HTTP layer: `create_flask_token`, `create_flask_breadcrumb`, `parse_list_request` (lists only), `service_cls.*`, `jsonify`. No payload mutation.
- List `GET` body is a **plain JSON array**. Request headers `offset` / `size` only. No `X-Pagination-*`, no `{items, has_more, next_cursor}`.
- Get-by-id `GET` body is the **document** (or 404). Not wrapped in an array.
- Deduplicate token/breadcrumb/jsonify in a private helper in the same module. Do not invent a second pagination stack.

### Factories and URL shapes (blueprint registered later with `/api/<collection>`)

| Factory | List GET `""` | Item GET | Service methods / constants |
|---------|---------------|----------|------------------------------|
| `create_resource_get_routes` | yes | `/<resource_id>` | `get_resources`, `get_resource`, `RESOURCE_LIST_*` |
| `create_path_get_routes` | yes | `/<path_id>` | `get_paths`, `get_path`, `PATH_LIST_*` |
| `create_plan_get_routes` | yes | `/<plan_id>` | `get_plans`, `get_plan`, `PLAN_LIST_*` |
| `create_profile_get_routes` | yes | `/<profile_id>` | `get_profiles`, `get_profile`, `PROFILE_LIST_*`. Do **not** add `/me` / `get_profile_by_token` |
| `create_notification_get_routes` | yes | none | `get_notifications`, `NOTIFICATION_LIST_ORDER` (empty filter spec if none) |
| `create_event_get_routes` | yes | none | `get_events`, `EVENT_LIST_*`. Do not expose `profile_id=` kwarg as a widen; optional query `profile_id` may **narrow** only if the service already supports it |
| `create_note_get_routes` | yes — required query `resource_id` (400 if missing) | none | `get_notes_for_resource`, `NOTE_LIST_*`. Do **not** expose `list_all_notes_for_resource` |
| `create_journey_get_routes` | **none** (Mentee owns `GET /api/journey` get-or-create) | `/<journey_id>` | `get_journey`. Do **not** expose `get_journey_progress` |
| `create_encounter_get_routes` | yes — required query `mentee_id` (400 if missing) | `/<encounter_id>` | `get_encounters_for_mentee`, `get_encounter`. Do **not** expose `get_recent_encounter` |
| `create_mentee_get_routes` | none | `/<profile_id>` | `get_mentee` |
| `create_aggregation_get_routes` | none | `/<resource_id>` | `get_aggregation_for_resource` (plain aggregation doc, not `get_aggregation_detail`) |
| `create_external_event_get_routes` | none | `/<event_id>` | `get_external_event` |

Do **not** add HTTP for `get_resources_by_ids`, `get_journey_progress`, `get_profile_by_token`, `get_recent_encounter`.

Put factories in `api_utils/routes/shared_get_routes.py` (one module). Export them from `api_utils.routes` if you add `api_utils/routes/__init__.py` exports; also re-export from `api_utils/__init__.py` next to `create_config_routes`.

## Goals

- Twelve `create_*_get_routes(service_cls, *, name=...)` factories as in the table.
- Flask test-client unit tests mock `service_cls` methods: list returns `[]` or a one-element list; body `isinstance(..., list)`; get-by-id 404 path via `HTTPNotFound`; missing `resource_id` / `mentee_id` → 400; unauthenticated token helper failure still mapped by `handle_route_exceptions`.
- Passing a **subclass** is what the route calls (`FakeResourceService.get_resources` not the shared class).
- No version bump.

## Testing Expectations

- `PYTHONPATH=. pipenv run pytest tests/routes/test_shared_get_routes.py`
- `pipenv run test`
- `pipenv run lint` — R084 files `black`-clean; ignore pre-existing lint elsewhere
- `pipenv run build`

## Outputs

- `api_utils/routes/shared_get_routes.py` — new
- `api_utils/routes/__init__.py` — export factories if this file is used
- `api_utils/__init__.py` — export `create_*_get_routes`
- `tests/routes/test_shared_get_routes.py` — new

The agent must not update files outside this list. Sample server wiring is R085. README is R087.

## Execution Notes

**Approach**: Added `api_utils/routes/shared_get_routes.py` with twelve `create_*_get_routes(service_cls, *, name=...)` factories. Private helpers `_auth_context`, `_json_ok`, and `_module_attr` deduplicate token/breadcrumb/jsonify and resolve `*_LIST_*` constants from the service class MRO. List routes use `parse_list_request` (or `parse_pagination_headers` for encounter); note/encounter lists return 400 when required query params are missing. Re-exported all factories from `api_utils/routes/__init__.py` and `api_utils/__init__.py`.

**Tests**: `tests/routes/test_shared_get_routes.py` — 12 tests covering list array bodies, get-by-id success/404, missing `resource_id`/`mentee_id` → 400, subclass dispatch, token failure → 401, and smoke coverage for all factory groups.

**Results**: `PYTHONPATH=. pipenv run pytest tests/routes/test_shared_get_routes.py` — 12 passed; `pipenv run test` — 237 passed; R084 files black-clean; `pipenv run build` — success.
