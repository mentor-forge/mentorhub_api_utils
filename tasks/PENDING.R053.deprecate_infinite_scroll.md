# R053 – Deprecate execute_infinite_scroll_query

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R055_add_event_service_list`  
**Description**: Mark `execute_infinite_scroll_query` as deprecated, document the replacement Get List pattern in README, and retain tests until downstream APIs migrate off infinite scroll.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/infinite_scroll.py`
- `api_utils/mongo_utils/list_query.py` — replacement pattern
- `tasks/_PLANNING.md` § Downstream follow-on issues — mentor_api and coordinator/customer APIs still use infinite scroll locally
- **Orchestration prerequisite**: `R050`, `R051`, `R052`, and `R055` must be Shipped before running this task (in addition to **Depends On** `R055`).

**Policy**: Do **not** delete `execute_infinite_scroll_query` or its tests in this task — downstream repos need a migration window. Add `DeprecationWarning` in docstring and optionally at runtime on first call.

## Goals

- `execute_infinite_scroll_query` module docstring and function docstring state deprecation; point to `list_query.execute_list_query`, `list_query.build_sort_by` / `order_spec`, and `flask_utils.list_request.parse_list_request`
- `README.md` documents standardized Get List pattern (header pagination + query filters); notes infinite scroll is legacy
- `docs/openapi.yaml` (if present in this repo) updated or annotated if it references infinite scroll
- `api_utils/mongo_utils/__init__.py` still exports `execute_infinite_scroll_query` (no breaking removal)
- Existing `tests/mongo_utils/test_infinite_scroll.py` continue to pass unchanged

## Testing Expectations

- `pipenv run test tests/mongo_utils/test_infinite_scroll.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/mongo_utils/infinite_scroll.py` — deprecation notice
- `README.md` — Get List pattern documentation
- `docs/openapi.yaml` — update if applicable

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
