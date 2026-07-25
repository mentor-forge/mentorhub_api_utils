# R064 – Harvest MenteeService into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Move `MenteeService` from `mentorhub_mentor_api/src/services/mentee_service.py` into `api_utils.services.mentee_service`, preserving behavior exactly (get-with-create-if-missing, update, mentor/admin RBAC, ObjectId handling). Port the mentor-API unit tests. No cross-service dependencies; can run in parallel with R062/R063.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Source service: `../mentorhub_mentor_api/src/services/mentee_service.py`
- Source tests: `../mentorhub_mentor_api/test/services/test_mentee_service.py`
- Target: `api_utils/services/mentee_service.py`
- Target tests: `tests/services/test_mentee_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R046.harvest_journey_service.md` — harvest pattern reference
- `../mentorhub_mentor_api/src/services/mentee_service.py`
- `../mentorhub_mentor_api/test/services/test_mentee_service.py`
- `api_utils/config/config.py` — `MENTEE_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN` (already present)

### Behavior to preserve

- Module-level `RESTRICTED_FIELDS = ["_id", "created", "saved"]`.
- `_check_permission(token, operation)` — require the `mentor` **or** `admin` role via shared `Config` role constants; otherwise `HTTPForbidden`.
- `_to_object_id(value, label)` — `HTTPBadRequest` on invalid `ObjectId`.
- `_default_document(profile_object_id, breadcrumb)` — schema-valid default (`profile_id` ObjectId, `status="active"`, empty text fields, `created`/`saved` breadcrumbs); omit optional `name`/`next_appointment`/`schedule`.
- `get_mentee(profile_id, token, breadcrumb)` — look up by `profile_id`; **create-if-missing** default doc and return it.
- `update_mentee(mentee_id, data, token, breadcrumb)` — restricted-field guard; stamp `saved`; `HTTPNotFound` when missing.
- All MongoDB I/O via **`MongoIO`** convenience methods only (no direct PyMongo).

## Goals

- `api_utils.services.mentee_service.MenteeService` matches Mentor API behavior exactly.
- Mentor-API unit tests ported to `tests/services/test_mentee_service.py` with patch targets rewritten to `api_utils.services.mentee_service.*`.
- Full test suite and build remain green.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db`
- `pipenv run test tests/services/test_mentee_service.py`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/mentee_service.py` — new harvested service
- `tests/services/test_mentee_service.py` — ported unit tests

The agent must not update files outside this list. (Package export is handled in R066.)

## Execution Notes

- Copied `MenteeService` verbatim into `api_utils/services/mentee_service.py` (source used only `api_utils`/`bson` imports; no `src.services.*` dependencies).
- Behavior preserved exactly: `RESTRICTED_FIELDS`, mentor/admin `_check_permission`, `_to_object_id` (`HTTPBadRequest`), `_default_document` (schema-valid defaults; optional fields omitted), `get_mentee` (create-if-missing), `update_mentee` (restricted-field guard + `saved` stamp + `HTTPNotFound`).
- Ported 14 unit tests to `tests/services/test_mentee_service.py` with patch targets rewritten `src.services.mentee_service.*` → `api_utils.services.mentee_service.*`.
- `pipenv run test tests/services/test_mentee_service.py`: passed; full suite `pipenv run test`: **232 passed**, 6 deselected.
- `pipenv run build`: succeeded. New files `black`-formatted (pre-existing whole-repo lint drift unchanged, out of scope).
