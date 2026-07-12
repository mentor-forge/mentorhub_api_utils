# R051 – Add standardized Get List to PathService.get_paths

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Extend `PathService.get_paths` with offset/size pagination and optional `name` contains filter, using the shared list-query utilities.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/list_query.py` — R049 utilities
- `api_utils/services/path_service.py` — `get_paths(token, breadcrumb)` returns **all** paths today
- `../mentorhub_mentor_api/src/services/path_service.py` — local mentor copy supports optional `name` contains filter via regex in `match`
- `tests/services/test_path_service.py`

**Breaking change**: Adding pagination with defaults `offset=0`, `size=20` changes behavior for callers that expect the full collection (e.g. mentee `GET /api/path`). Document downstream adoption in `tasks/_PLANNING.md` § Downstream follow-on issues. Consider supporting `size=None` meaning “return all” only if needed for composite callers — default should remain `20` per platform contract.

## Goals

- `PathService.get_paths(token, breadcrumb, offset=DEFAULT_OFFSET, size=DEFAULT_SIZE, filters=None, sort_by=None)`:
  - Paginated via `execute_list_query`
  - `PATH_LIST_ORDER` default `name` asc; `allowed` only `name` (`asc`/`desc`) — fixed-sort endpoint with standard order-by interface
  - Optional `filters` with `name` contains (case-insensitive regex)
  - RBAC unchanged (authenticated read)
- Unit tests: pagination window; name filter; default offset/size; order-by default and `sort_by=name&order=desc`

## Testing Expectations

- `pipenv run test tests/services/test_path_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/path_service.py`
- `tests/services/test_path_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
