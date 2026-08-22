# R078 – Strip Journey control POST/PATCH/mutate from shared JourneyService

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R075_classmethod_and_data_boundary_contract`  
**Description**: Mentee **controls** Journey. Shared `JourneyService` keeps consume GETs (and mentor/admin progress aggregation). Remove clone-on-read, enrich, create, patch, and mutate — those bodies are already captured in `ISSUE.journey_api.md` for the Mentee API subclass.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml` — Mentee **controls** Journey; Customer and Discovery **consume** Journey
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/ISSUE.journey_api.md` — harvest-back source; **do not rewrite unless a kept helper signature changes**
- `api_utils/services/journey_service.py`
- `tests/services/test_journey_service.py`
- `tests/services/test_journey_service_integration.py`

### Keep on shared `JourneyService`

| Member | Role |
|--------|------|
| `TEMPLATE_JOURNEY_ID` | Constant for the Mentee subclass clone |
| `_check_permission` | **read** only (authenticated consume). Drop update/mutate/complete branches |
| `_validate_object_id`, `_oid` | Id helpers used by GET |
| `get_journey` | By id; 404 if missing; no create |
| `get_journey_progress` | Consume-side counts with mentor/admin RBAC (already implemented) |

`get_journey` must **not** clone the template. Missing document → `HTTPNotFound`. The Mentee subclass `get_my_journey` catches that and clones.

### Remove from shared (already in `ISSUE.journey_api.md`)

- `RESTRICTED_UPDATE_FIELDS`, `_validate_update_data`
- `_clone_template`, `get_my_journey`, `get_my_journey_detail`
- `create_journey`, `update_journey`
- `_resource_id_in_next`, `_remove_resource_from_next`, `_find_now_entry`, `_event_token`
- `advance_resource`, `complete_resource`
- `_path_id_in_later`, `_module_to_next_module`, `_module_name_in_next`, `_load_path_and_journey`
- `promote_path_to_next`, `promote_module_to_next`

Delete corresponding unit/integration tests from this repo. Do not port tests here — they belong in `mentorhub_mentee_api` with the subclass.

If the live method body differs from `ISSUE.journey_api.md` after R075 classmethod conversion, update **only** the ISSUE code fences so the harvest-back still matches what was removed (classmethod/`cls` form).

## Goals

- Shared JourneyService is read-only consume (`get_journey`, `get_journey_progress`).
- No Journey writes, get-or-create, or profile enrich remain in api_utils.
- `TEMPLATE_JOURNEY_ID` remains exported.
- Tests that remain cover get-by-id, 404, and progress RBAC/counts only.

## Testing Expectations

- `pipenv run test tests/services/test_journey_service.py tests/services/test_journey_service_integration.py`
- `pipenv run test`
- `pipenv run lint` — R078 files `black`-clean
- `pipenv run build`

## Outputs

- `api_utils/services/journey_service.py`
- `tests/services/test_journey_service.py`
- `tests/services/test_journey_service_integration.py`
- `tasks/ISSUE.journey_api.md` — only if harvested code must be synced to classmethod form

The agent must not update files outside this list.

## Execution Notes

Stripped `JourneyService` to consume GETs only: kept `TEMPLATE_JOURNEY_ID`, read-only `_check_permission`, id helpers, `get_journey`, and `get_journey_progress`. Removed all mutation/clone/enrich methods and unused imports (`copy`, write-path `encode_document` usage).

Replaced unit tests: added `get_journey` success/404/error cases; retained `TestJourneyProgress` RBAC/count suite; removed mutation/clone/detail tests.

Replaced integration tests: `get_journey` by seeded template id and 404 for missing id; removed clone/advance/complete/promote flows.

`ISSUE.journey_api.md` harvest-back already in classmethod/subclass form — no sync required.
