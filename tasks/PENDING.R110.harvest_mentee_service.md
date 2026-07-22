# R110 – Harvest `MenteeService` into `api_utils.services`

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Move the Mentee (mentor-notes) domain from
`mentorhub_mentor_api/src/services/mentee_service.py` into a new shared
`api_utils.services.MenteeService`, preserving behavior exactly — including the
read "create-if-missing" pattern the Profile detail composite (R120) relies on.

## Context / Input files

- `mentorhub_mentor_api/src/services/mentee_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/config/config.py` (`MENTEE_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN`)
- `mentorhub_api_utils/api_utils/mongo_utils/mongo_io.py`
- `mentorhub_mentor_api/tasks/SHIPPED.L020.create_mentee_service_and_route.md`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Create `api_utils/services/mentee_service.py` with `MenteeService`:
  - `get_mentee(profile_id, token, breadcrumb)` — mentor/admin RBAC; convert
    `profile_id` to `ObjectId` (`HTTPBadRequest` on invalid); look up by
    `profile_id`; if none, create and return a schema-valid default document via
    `_default_document` (`status="active"`, empty text fields, `created`/`saved`
    breadcrumbs), then re-read and return it.
  - `update_mentee(mentee_id, data, token, breadcrumb)` — mentor/admin RBAC;
    restricted-field guard; convert `mentee_id` to `ObjectId`; `$set` remaining
    fields + `saved`; `HTTPNotFound` when missing.
  - Preserve helpers `_collection_name`, `_check_permission`, `_to_object_id`,
    `_validate_update_data`, `_default_document`, and the module-level
    `RESTRICTED_FIELDS` exactly.
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Create**: `api_utils/services/mentee_service.py`
- **Modify**: `api_utils/services/__init__.py` (export `MenteeService`)
- **Create**: `tests/services/test_mentee_service.py`
  (get-existing, create-if-missing default shape, invalid id, update RBAC +
  restricted-field guard + not-found)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040. Should land before **R120** (Profile detail composite
  calls `get_mentee`). Independent of R050/R060/R070/R080.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Created shared `MenteeService` (get create-if-missing, update) + helpers.
- [ ] Exported from `api_utils.services`.
- [ ] Added tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
