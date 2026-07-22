# R060 – Extend shared `EventService` with by-id read + create

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Extend `api_utils.services.EventService` so the Event domain is fully upstream:
add `get_event` (by-id) and `create_event` (with ObjectId encoding) currently in
`mentorhub_mentor_api/src/services/event_service.py`, alongside the existing
`get_events` list read. Preserve behavior exactly.

## Context / Input files

- `mentorhub_mentor_api/src/services/event_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/services/event_service.py` (baseline from R040)
- `mentorhub_api_utils/api_utils/mongo_utils/encode_properties.py` (`encode_document`)
- `mentorhub_api_utils/api_utils/config/config.py` (`EVENT_COLLECTION_NAME`)
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Add to the shared `EventService`:
  - `create_event(data, token, breadcrumb)` — drop client `_id`, call
    `encode_document(data, ["_id", "profile_id"], [])` so nested
    `context.profile_id` is coerced to BSON `ObjectId` for the `$jsonSchema`
    validator, stamp the `created` breadcrumb (Event has **no** `saved` field),
    `create_document` into `EVENT_COLLECTION_NAME`, return new id.
  - `get_event(event_id, token, breadcrumb)` — by-id read; `HTTPNotFound` when
    missing.
- Preserve `ID_PROPERTIES = ["_id", "profile_id"]` / `DATE_PROPERTIES = []`
  exactly as in the mentor source.
- Keep the existing `get_events` list read (offset/size, `type` filter,
  `EVENT_LIST_ORDER`, optional `profile_id` scope) and `EVENT_LIST_FILTERS`/
  `EVENT_LIST_ORDER` unchanged.
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Modify**: `api_utils/services/event_service.py`
- **Modify**: `api_utils/services/__init__.py` (as needed)
- **Create/Modify**: `tests/services/test_event_service.py` (create/get/list, ObjectId encoding)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040. Independent of R050/R070/R080/R110 (may run concurrently).

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Added `create_event` (ObjectId encode) + `get_event` upstream.
- [ ] Preserved list read + specs.
- [ ] Added/updated tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
