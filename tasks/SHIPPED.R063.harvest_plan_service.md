# R063 – Harvest PlanService into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Move `PlanService` from `mentorhub_mentor_api/src/services/plan_service.py` into `api_utils.services.plan_service`, preserving behavior exactly. Port the mentor-API unit tests. Plan has no cross-service dependencies, so this can run in parallel with R062/R064.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Source service: `../mentorhub_mentor_api/src/services/plan_service.py`
- Source tests: `../mentorhub_mentor_api/test/services/test_plan_service.py`
- Target: `api_utils/services/plan_service.py`
- Target tests: `tests/services/test_plan_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R046.harvest_journey_service.md` — harvest pattern reference
- `tasks/SHIPPED.R051.refactor_path_service_list.md` — shared list-query (`offset`/`size`, `sort_by`/`order`, filters) reference
- `../mentorhub_mentor_api/src/services/plan_service.py`
- `../mentorhub_mentor_api/test/services/test_plan_service.py`
- `api_utils/mongo_utils/list_query.py` — `DEFAULT_OFFSET`, `DEFAULT_SIZE`, `build_match_filter`, `build_sort_by`, `execute_list_query`
- `api_utils/config/config.py` — `PLAN_COLLECTION_NAME` (already present)

### Behavior to preserve

- Module-level `PLAN_LIST_FILTERS` (`name` → contains) and `PLAN_LIST_ORDER` (default `name` asc; allowed `name` asc/desc).
- `create_plan(data, token, breadcrumb)` — strip client `_id`; stamp `created`/`saved` from breadcrumb; return new id.
- `get_plans(token, breadcrumb, offset, size, filters, sort_by)` — shared header pagination + `sort_by`/`order` + optional `name` contains filter via `execute_list_query`; returns a plain list.
- `get_plan(plan_id, token, breadcrumb)` — `HTTPNotFound` when missing.
- `update_plan(plan_id, data, token, breadcrumb)` — restricted-field guard (`_id`, `created`, `saved`); stamp `saved`; `HTTPNotFound` when missing.
- `_check_permission` is currently an authenticate-only placeholder — **preserve as-is** (do not add new RBAC).
- All MongoDB I/O via **`MongoIO`** convenience methods only (no direct PyMongo).

## Goals

- `api_utils.services.plan_service.PlanService` matches Mentor API behavior byte-for-byte in semantics (create/list/get/update, list conventions, restricted-field guard).
- Mentor-API unit tests ported to `tests/services/test_plan_service.py` with patch targets rewritten to `api_utils.services.plan_service.*`.
- Full test suite and build remain green.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db`
- `pipenv run test tests/services/test_plan_service.py`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/plan_service.py` — new harvested service
- `tests/services/test_plan_service.py` — ported unit tests

The agent must not update files outside this list. (Package export is handled in R066.)

## Execution Notes

- Copied `PlanService` verbatim into `api_utils/services/plan_service.py` (source already used `api_utils`/`api_utils.mongo_utils.list_query` imports and had no `src.services.*` dependencies, so no import rewrites in the service itself).
- Behavior preserved exactly: `PLAN_LIST_FILTERS`/`PLAN_LIST_ORDER`, authenticate-only `_check_permission` placeholder, create (`_id` strip + `created`/`saved` stamp), `get_plans` (shared header pagination + `name` contains), `get_plan` (404), `update_plan` (restricted-field guard + `saved` stamp).
- Ported 18 unit tests to `tests/services/test_plan_service.py` with patch targets rewritten `src.services.plan_service.*` → `api_utils.services.plan_service.*` (includes checklist passthrough coverage).
- `pipenv run test tests/services/test_plan_service.py`: passed; full suite `pipenv run test`: **217 passed**, 6 deselected.
- `pipenv run build`: succeeded. Both new files are `black`-clean (pre-existing whole-repo lint drift unchanged, out of scope).
