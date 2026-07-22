# R050 – Extend shared `ResourceService` with CRUD

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Make `api_utils.services.ResourceService` a **full-domain** service by adding
the create/read/update CRUD that currently lives locally in
`mentorhub_mentor_api/src/services/resource_service.py`, alongside the existing
`get_resources` list read. Preserve behavior exactly.

## Context / Input files

- `mentorhub_mentor_api/src/services/resource_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/services/resource_service.py` (baseline from R040)
- `mentorhub_api_utils/api_utils/config/config.py` (`RESOURCE_COLLECTION_NAME`)
- `mentorhub_api_utils/api_utils/mongo_utils/mongo_io.py`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Add to the shared `ResourceService`:
  - `create_resource(data, token, breadcrumb)` — drop client `_id`, stamp
    `created`/`saved` breadcrumbs, `create_document` into
    `RESOURCE_COLLECTION_NAME`, return new id.
  - `get_resource(resource_id, token, breadcrumb)` — by-id read; `HTTPNotFound`
    when missing.
  - `update_resource(resource_id, data, token, breadcrumb)` — restricted-field
    guard (`_id`/`created`/`saved`), `$set` remaining fields + `saved`
    breadcrumb; `HTTPNotFound` when missing.
- Keep the existing `get_resources` list read and
  `RESOURCE_LIST_FILTERS`/`RESOURCE_LIST_ORDER` unchanged.
- Preserve the `_check_permission` placeholder (authenticated-only) and
  `_validate_update_data` semantics exactly as in the mentor source.
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Modify**: `api_utils/services/resource_service.py`
- **Modify**: `api_utils/services/__init__.py` (ensure CRUD-capable service exported)
- **Create/Modify**: `tests/services/test_resource_service.py` (CRUD + list coverage)

## Testing expectations

- `pipenv run db`, then `pipenv run test` (unit + MongoIO integration) green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040. Independent of R060/R070/R080/R110 (may run concurrently).

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Added `create_resource`/`get_resource`/`update_resource` upstream.
- [ ] Preserved list read + specs.
- [ ] Added/updated tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
