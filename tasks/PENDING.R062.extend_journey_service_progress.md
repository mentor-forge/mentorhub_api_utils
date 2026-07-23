# R062 – Extend shared JourneyService with get_journey_progress

**Status**: Pending  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Add the mentor-dashboard aggregation `get_journey_progress` (active-journey resource counts by scope) to `api_utils.services.journey_service.JourneyService`. This is the one Journey method the Mentor API still keeps locally; harvesting it upstream unblocks `ProfileService` (R065). Port the mentor-API unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Source service: `../mentorhub_mentor_api/src/services/journey_service.py`
- Source tests: `../mentorhub_mentor_api/test/services/test_journey_service.py`
- Target: `api_utils/services/journey_service.py`
- Target tests: `tests/services/test_journey_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R046.harvest_journey_service.md` — original JourneyService harvest pattern
- `tasks/SHIPPED.R060.harvest_journey_get_my_journey_detail.md` — most recent additive Journey harvest
- `../mentorhub_mentor_api/src/services/journey_service.py` — local mentor Journey service (source of `get_journey_progress`)
- `../mentorhub_mentor_api/test/services/test_journey_service.py`
- `api_utils/services/journey_service.py` — existing shared class (`_check_permission`, advance/complete, promote, `get_my_journey_detail`)
- `api_utils/config/config.py` — `JOURNEY_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN` (already present)

### Behavior to harvest

| Method | Behavior |
|--------|----------|
| **`get_journey_progress(profile_id, token, breadcrumb)`** | Read the mentee's **active** Journey (`{"profile_id": profile_id, "status": "active"}`). Return `{"library": int, "now": int, "next": int}`: `library`/`now` count their resource entries directly; `next` **sums** the resource entries across all Next topics. Return `{"library": 0, "now": 0, "next": 0}` when there is no active journey. Mentor/admin RBAC via existing `_check_permission(token, "read")`. |

### Merge rules

- Add as a **`JourneyService` static method** — do not create a new class.
- Reuse the existing `JourneyService._check_permission`; do not duplicate role logic.
- All MongoDB I/O via **`MongoIO`** convenience methods only (no direct PyMongo).
- Do **not** change any existing Journey method return shapes.

## Goals

- `api_utils.services.JourneyService.get_journey_progress` matches the Mentor API local behavior exactly (scope counts + zero default).
- Mentor-API unit tests for progress ported to `tests/services/test_journey_service.py` with patch targets rewritten from `src.services.journey_service.*` to `api_utils.services.journey_service.*`.
- Full test suite and build remain green.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db` — start the backing database (required for tests)
- `pipenv run test tests/services/test_journey_service.py` — includes new progress coverage
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/journey_service.py` — add `get_journey_progress`
- `tests/services/test_journey_service.py` — add ported progress tests

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
