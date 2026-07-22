# R120 – Harvest `ProfileService` into `api_utils.services`

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Move the Profile domain from
`mentorhub_mentor_api/src/services/profile_service.py` into a new shared
`api_utils.services.ProfileService`, preserving behavior exactly — the token
resolver, the Mentor Dashboard composite, the Profile detail composite, and the
Properties-hub aggregation, all assembled via service-to-service calls.

## Context / Input files

- `mentorhub_mentor_api/src/services/profile_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/services/journey_service.py` (from R080)
- `mentorhub_api_utils/api_utils/services/mentee_service.py` (from R110)
- `mentorhub_api_utils/api_utils/services/encounter_service.py` (from R100)
- `mentorhub_api_utils/api_utils/config/config.py` (`PROFILE_COLLECTION_NAME`, `JOURNEY_COLLECTION_NAME`, `RESOURCE_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN`)
- `mentorhub_mentor_api/tasks/SHIPPED.L030.update_profile_service_composite_detail.md`
- `mentorhub_mentor_api/tasks/SHIPPED.L040.refactor_profile_service_into_journey_encounter_services.md`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Create `api_utils/services/profile_service.py` with `ProfileService`:
  - `get_profile_by_token(token, breadcrumb)` — resolve the caller Profile whose
    `name` == token `user_id`; return the doc or `None`. (No RBAC gate — this is
    the service-to-service identity resolver used by Encounter's owner check.)
  - `get_profiles(token, breadcrumb)` — mentor/admin RBAC; build the Mentor
    Dashboard: resolve the caller Profile, one card per assigned mentee
    (`match={"mentor_id": <caller _id>}`, name-asc) with `_id`/`name`/
    `description`, `progress` via `JourneyService.get_journey_progress`, and
    `last_encounter` via `EncounterService.get_recent_encounter`; empty list when
    no caller Profile.
  - `get_profile(profile_id, token, breadcrumb)` — mentor/admin RBAC; composite
    detail `{"profile": ..., "mentee": ..., "encounters": [...]}` via
    `MenteeService.get_mentee` and
    `EncounterService.get_encounters_for_mentee`; `HTTPNotFound` when Profile
    missing.
  - `get_profile_properties(profile_id, token, breadcrumb)` — mentor/admin RBAC;
    the Profile/Journey/Resource/Encounter aggregation (status summary,
    sites_and_links, resource_usage, celebrations, mentor_history, journey) as in
    the source.
  - Preserve helpers `_check_permission`, `_resource_ref`, `_load_resource`,
    `_mentor_history` exactly.
- Use **lazy imports** for Journey/Mentee/Encounter inside methods to avoid the
  Profile↔Encounter import cycle (mirroring the mentor source).
- MongoIO-only access; no direct PyMongo (composites use service-to-service
  calls, not cross-collection reads, except the Journey/Resource reads the
  Properties aggregation already performs directly in the source).

## Files to modify / create

- **Create**: `api_utils/services/profile_service.py`
- **Modify**: `api_utils/services/__init__.py` (export `ProfileService`)
- **Create**: `tests/services/test_profile_service.py`
  (token resolver, dashboard composite, detail composite, properties
  aggregation, RBAC, not-found)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040, R080 (Journey), R110 (Mentee). Composes with **R100**
  (Encounter) via lazy import — the dashboard/detail composites call
  `get_recent_encounter`/`get_encounters_for_mentee`, and Encounter's owner
  patch calls `get_profile_by_token`. Recommended sequence: R080/R110 →
  **R120** → R100, treating R100+R120 as a co-landing cluster for final tests.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Created shared `ProfileService` (token resolver, dashboard, detail,
      properties) + helpers.
- [ ] Used lazy imports for Journey/Mentee/Encounter (no import cycle).
- [ ] Exported from `api_utils.services`.
- [ ] Added tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
