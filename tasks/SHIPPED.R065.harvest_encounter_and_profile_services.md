# R065 – Harvest Encounter and Profile services into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R062_extend_journey_service_progress`, `R063_harvest_plan_service`, `R064_harvest_mentee_service`  
**Description**: Move `EncounterService` and `ProfileService` from `mentorhub_mentor_api/src/services/` into `api_utils.services`, preserving behavior exactly. These two are **mutually dependent composites** (Encounter's owner check calls `ProfileService.get_profile_by_token`; Profile's dashboard/detail call `EncounterService`), so they are harvested together in one task. Port the mentor-API unit tests for both.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Source services: `../mentorhub_mentor_api/src/services/encounter_service.py`, `../mentorhub_mentor_api/src/services/profile_service.py`
- Source tests: `../mentorhub_mentor_api/test/services/test_encounter_service.py`, `../mentorhub_mentor_api/test/services/test_profile_service.py`
- Targets: `api_utils/services/encounter_service.py`, `api_utils/services/profile_service.py`
- Target tests: `tests/services/test_encounter_service.py`, `tests/services/test_profile_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R046.harvest_journey_service.md` — harvest + lazy-import pattern reference
- `tasks/PENDING.R062.extend_journey_service_progress.md` — provides `JourneyService.get_journey_progress`
- `tasks/PENDING.R063.harvest_plan_service.md` — provides `PlanService`
- `tasks/PENDING.R064.harvest_mentee_service.md` — provides `MenteeService`
- `../mentorhub_mentor_api/src/services/encounter_service.py`
- `../mentorhub_mentor_api/src/services/profile_service.py`
- `../mentorhub_mentor_api/test/services/test_encounter_service.py`
- `../mentorhub_mentor_api/test/services/test_profile_service.py`
- `api_utils/mongo_utils/__init__.py` — `encode_document`
- `api_utils/config/config.py` — `ENCOUNTER_COLLECTION_NAME`, `PROFILE_COLLECTION_NAME`, `JOURNEY_COLLECTION_NAME`, `RESOURCE_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN` (all present)

### Import rewrites (critical)

Every intra-repo `from src.services.<x> import <Y>` becomes `from api_utils.services.<x> import <Y>`:

- `encounter_service.py`: top-level `from src.services.plan_service import PlanService` → `from api_utils.services.plan_service import PlanService`; lazy `from src.services.profile_service import ProfileService` → `api_utils.services.profile_service`.
- `profile_service.py`: lazy imports of `JourneyService`, `EncounterService`, `MenteeService` → their `api_utils.services.*` modules. **Keep them lazy** (inside the methods) to preserve the cycle-breaking behavior.

### EncounterService behavior to preserve

- `_check_permission(token, operation, breadcrumb, encounter=None)` — admin passes; else require `mentor`; when `encounter` supplied, resolve caller via `ProfileService.get_profile_by_token` and require caller Profile `_id == encounter.mentor_id` (owner-or-admin).
- `_validate_update_data` — restricted fields `_id`/`created`/`saved`.
- `_build_agenda_from_plan(plan)` — agenda items `{"step": <entry>, "checked": False}` from `plan["steps"]` (fallback `plan["checklist"]`); `[]` when empty.
- `create_encounter` — fetch referenced Plan via `PlanService.get_plan` (missing → `HTTPNotFound`), auto-fill `agenda` (override client value), strip `_id`, `encode_document(data, ["mentor_id", "mentee_id", "plan_id"], [])`, stamp `created`/`saved`.
- `_normalize_mentee_id` — tolerant string/`ObjectId` coercion.
- `get_recent_encounter` — latest-`date` summary (`_id`,`date`,`tldr`,`summary`) or `None`.
- `get_encounters_for_mentee` — `date`-desc; **optional** `offset`/`size` (full list when omitted, for composite callers).
- `get_encounter` / `update_encounter` — 404 before ownership check; owner-or-admin patch; restricted-field guard; stamp `saved`.

### ProfileService behavior to preserve

- `_check_permission` — mentor/admin.
- `get_profile_by_token(token, breadcrumb)` — resolve caller Profile by `name == token.user_id`; `None` when absent.
- `get_profiles(token, breadcrumb)` — Mentor Dashboard: one card per assigned mentee (`mentor_id == caller._id`, name asc) with `progress` (`JourneyService.get_journey_progress`) and `last_encounter` (`EncounterService.get_recent_encounter`).
- `get_profile(profile_id, token, breadcrumb)` — composite `{profile, mentee, encounters}` via `MenteeService.get_mentee` + `EncounterService.get_encounters_for_mentee`; 404 when Profile missing.
- `get_profile_properties(profile_id, token, breadcrumb)` — Journey/Resource/Encounter aggregation (sites_and_links, resource_usage, celebrations, status_summary, mentor_history) with `_resource_ref`/`_load_resource`/`_mentor_history` helpers preserved.
- All MongoDB I/O via **`MongoIO`** convenience methods only (no direct PyMongo).

## Goals

- `api_utils.services.EncounterService` and `api_utils.services.ProfileService` match Mentor API behavior exactly, including the lazy service-to-service composition (no import cycles at module load).
- Mentor-API unit tests ported to `tests/services/test_encounter_service.py` and `tests/services/test_profile_service.py`, with all patch targets rewritten to `api_utils.services.*`.
- Full test suite and build remain green.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db`
- `pipenv run test tests/services/test_encounter_service.py tests/services/test_profile_service.py`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/encounter_service.py` — new harvested service
- `api_utils/services/profile_service.py` — new harvested service
- `tests/services/test_encounter_service.py` — ported unit tests
- `tests/services/test_profile_service.py` — ported unit tests

The agent must not update files outside this list. (Package export is handled in R066.)

## Execution Notes

- Harvested `EncounterService` → `api_utils/services/encounter_service.py` and `ProfileService` → `api_utils/services/profile_service.py`, preserving behavior exactly.
- Import rewrites applied: `encounter_service` top-level `from src.services.plan_service import PlanService` → `api_utils.services.plan_service`; lazy `ProfileService` import → `api_utils.services.profile_service`. `profile_service` lazy imports of `JourneyService`/`EncounterService`/`MenteeService` → `api_utils.services.*` (kept lazy to preserve cycle-breaking).
- Behavior preserved: Encounter owner-or-admin RBAC (via `ProfileService.get_profile_by_token`), agenda auto-fill from Plan checklist, `_normalize_mentee_id`, optional-pagination `get_encounters_for_mentee`, 404-before-ownership on update; Profile dashboard/detail/properties composites with service-to-service calls.
- Ported unit tests to `tests/services/test_encounter_service.py` and `tests/services/test_profile_service.py`, patch targets rewritten to `api_utils.services.*` (Encounter owner tests patch `api_utils.services.profile_service.ProfileService.get_profile_by_token`; Profile tests patch collaborators at their home modules).
- Full suite `pipenv run test`: **275 passed**, 6 deselected. `pipenv run build`: succeeded. All 4 new files `black`-formatted (pre-existing whole-repo lint drift unchanged, out of scope).
