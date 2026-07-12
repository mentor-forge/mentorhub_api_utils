# R055 – Add standardized Get List to EventService

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Add `EventService.get_events` using the shared list-query utilities (offset/size pagination, `type` in_list filter, optional profile scope) so mentor API can drop local infinite-scroll list logic.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/list_query.py` — R049 utilities
- `api_utils/services/event_service.py` — `create_event` only today (harvested POST-only mentee contract)
- `../mentorhub_mentor_api/src/services/event_service.py` — legacy `get_events` via `execute_infinite_scroll_query`; reference for read RBAC and sort fields
- `../mentorhub_mentor_api/src/routes/event_routes.py` — infinite-scroll query params to replace downstream
- `tasks/SHIPPED.R020.add_event_type_constants_config.md` — `EVENT_TYPE_*` config constants for filter validation
- `tests/services/test_event_service.py`

**Mentee API note**: `mentorhub_mentee_api` removed `GET /api/event` (POST-only). This task adds list support to the **shared library** for mentor and other admin-style APIs; it does not require mentee route changes.

### Target `get_events` contract

```python
EventService.get_events(
    token,
    breadcrumb,
    offset=DEFAULT_OFFSET,
    size=DEFAULT_SIZE,
    filters=None,
    sort_by=None,
    *,
    profile_id=None,  # optional scope: match context.profile_id
)
```

| Concern | Convention |
|---------|------------|
| Pagination | `offset`/`size` kwargs (defaults `0`/`20`, max `100`) |
| Order by | `EVENT_LIST_ORDER` default `created.at_time` desc; allowed: `type`, `created.at_time` (each `asc`/`desc`) — replaces mentor infinite-scroll `sort_by`/`order` with standardized `order_spec` |
| `type` filter | Query `type=login,link` → `$in` on top-level `type` field |
| Profile scope | When `profile_id` kwarg or filter `profile_id` provided, add `match` on `context.profile_id` (ObjectId-encoded) |
| RBAC | Authenticated read (placeholder `_check_permission(token, "read")`; no extra role gate) |
| Response | Plain `list` of event documents (route layer returns JSON array) |

**Out of scope**: `get_event(event_id, ...)` by-id read — mentor keeps local implementation until a separate harvest task; this task is list-only.

## Goals

- `EventService.get_events(...)` implemented with `validate_pagination` and `execute_list_query`
- `EVENT_LIST_FILTERS` spec: `type` → `in_list` on `type`; optional `profile_id` → equals on `context.profile_id` (ObjectId)
- `EVENT_LIST_ORDER` spec per target contract above; `sort_by` kwarg accepts PyMongo sort list from `build_sort_by`
- Invalid `type` values in filter rejected with `HTTPBadRequest` when they are not members of configured `EVENT_TYPE_*` constants (or allow any string if configurator enum lookup is impractical — document choice in Execution Notes)
- Unit tests: pagination; `type` in_list filter; optional `profile_id` scope; **order-by default, custom, invalid**; RBAC smoke test
- `create_event` behavior unchanged

## Testing Expectations

- `pipenv run test tests/services/test_event_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/event_service.py`
- `tests/services/test_event_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
