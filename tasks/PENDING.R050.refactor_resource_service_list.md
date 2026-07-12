# R050 – Refactor ResourceService.get_resources to standardized Get List

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Replace Python-side slicing in `ResourceService.get_resources` with `execute_list_query`, add extensible query filters (`name`, `description`, `status`), and remove duplicated pagination helpers.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/list_query.py` — R049 utilities
- `api_utils/services/resource_service.py` — current `get_resources(token, breadcrumb, offset, size)`
- `tests/services/test_resource_service.py`

**Current behavior** (harvested from mentee API):

- Pagination: `offset`/`size` kwargs (defaults `0`/`20`, max size `100`)
- RBAC: non-admin excludes `status: archived`
- Sort: `name` ascending (becomes `RESOURCE_LIST_ORDER` default; client may select other allowed fields via `sort_by`/`order`)
- No query-parameter filters at service layer (route does not pass filters today)

**Breaking change assessment**: Adding optional `filters=None` kwarg is backward compatible. Changing default result set is **not** required. Removing module-level `DEFAULT_*` constants in favor of shared `list_query` constants may affect importers — re-export from `resource_service` or document migration in R054.

## Goals

- `ResourceService.get_resources(token, breadcrumb, offset=DEFAULT_OFFSET, size=DEFAULT_SIZE, filters=None, sort_by=None)`:
  - Uses `validate_pagination` and `execute_list_query` with MongoDB `skip`/`limit`
  - Applies base `match` for archived exclusion (non-admin) before filter merge
  - When `filters` is provided, merges `name`/`description` contains and `status` in_list per `RESOURCE_LIST_FILTERS` spec
  - When `sort_by` is `None`, uses `build_sort_by` with `RESOURCE_LIST_ORDER` default (`name` asc); when provided, `sort_by` is a pre-built PyMongo sort list from `parse_list_request` / `build_sort_by`
  - Define `RESOURCE_LIST_ORDER` with allowed fields: `name`, `description`, `status`, `created.at_time`, `saved.at_time` (each `asc`/`desc`)
- Remove duplicated `_validate_pagination` and local `DEFAULT_OFFSET`/`DEFAULT_SIZE`/`MAX_SIZE` if fully superseded by `list_query` (or thin-wrap shared constants)
- Unit tests updated: server-side pagination; filter tests; **order-by default, custom field/direction, invalid sort_by rejected**; archived RBAC unchanged

## Testing Expectations

- `pipenv run test tests/services/test_resource_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/resource_service.py`
- `tests/services/test_resource_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
