# R080 – Harvest `JourneyService` into `api_utils.services`

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Move the Learning Journey progress aggregation from
`mentorhub_mentor_api/src/services/journey_service.py` into a new shared
`api_utils.services.JourneyService`, preserving behavior exactly. This is
consumed by the Profile dashboard/properties composites (R120).

## Context / Input files

- `mentorhub_mentor_api/src/services/journey_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/config/config.py` (`JOURNEY_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN`)
- `mentorhub_api_utils/api_utils/mongo_utils/mongo_io.py`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Create `api_utils/services/journey_service.py` with `JourneyService`:
  - `get_journey_progress(profile_id, token, breadcrumb)` — mentor/admin RBAC;
    read the mentee's **active** Journey
    (`match={"profile_id": ..., "status": "active"}`); return
    `{"library": int, "now": int, "next": int}` where `library`/`now` count
    their resource entries and `next` sums resource entries across all Next
    topics; return zeros when no active journey exists.
  - Preserve `_check_permission` (mentor/admin) exactly.
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Create**: `api_utils/services/journey_service.py`
- **Modify**: `api_utils/services/__init__.py` (export `JourneyService`)
- **Create**: `tests/services/test_journey_service.py`
  (active/no-journey, per-scope counts, RBAC)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040. Should land before **R120** (Profile composites call it).
  Independent of R050/R060/R070/R110.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Created shared `JourneyService.get_journey_progress` with mentor/admin RBAC.
- [ ] Exported from `api_utils.services`.
- [ ] Added tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
