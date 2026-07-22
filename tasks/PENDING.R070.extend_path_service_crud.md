# R070 – Extend shared `PathService` with CRUD + RBAC

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Make `api_utils.services.PathService` a full-domain service by adding the
create/read/update CRUD (with mentor/admin RBAC on update) currently in
`mentorhub_mentor_api/src/services/path_service.py`, alongside the existing
`get_paths` list read. Preserve behavior exactly.

## Context / Input files

- `mentorhub_mentor_api/src/services/path_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/services/path_service.py` (baseline from R040)
- `mentorhub_api_utils/api_utils/config/config.py` (`PATH_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN`)
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Add to the shared `PathService`:
  - `create_path(data, token, breadcrumb)` — drop client `_id`, stamp
    `created`/`saved` breadcrumbs, `create_document` into `PATH_COLLECTION_NAME`,
    return new id.
  - `get_path(path_id, token, breadcrumb)` — by-id read; `HTTPNotFound` when
    missing.
  - `update_path(path_id, data, token, breadcrumb)` — restricted-field guard
    (`_id`/`created`/`saved`), `$set` remaining fields + `saved` breadcrumb;
    `HTTPNotFound` when missing.
- Preserve `_check_permission` semantics exactly: `update` requires
  `ROLE_MENTOR` **or** `ROLE_ADMIN`; `read`/`create` are authenticated-only.
- Keep the existing `get_paths` list read and
  `PATH_LIST_FILTERS`/`PATH_LIST_ORDER` unchanged.
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Modify**: `api_utils/services/path_service.py`
- **Modify**: `api_utils/services/__init__.py` (as needed)
- **Create/Modify**: `tests/services/test_path_service.py` (CRUD, update RBAC, list)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green (incl. mentor/admin update RBAC cases).
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040. Independent of R050/R060/R080/R110 (may run concurrently).

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Added `create_path`/`get_path`/`update_path` upstream with update RBAC.
- [ ] Preserved list read + specs.
- [ ] Added/updated tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
