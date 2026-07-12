# R041 – Harvest NoteService into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R040_scaffold_services_package`  
**Description**: Move `NoteService` from `mentorhub_mentee_api` into `api_utils.services.note_service` with unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

- Source: `../mentorhub_mentee_api/src/services/note_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_note_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `../mentorhub_mentee_api/src/services/note_service.py`
- `../mentorhub_mentee_api/test/services/test_note_service.py`
- `api_utils/mongo_utils/mongo_io.py`
- `api_utils/mongo_utils/encode_properties.py`

**NoteService surface** (from mentee API):

- `_check_permission(token, operation)` — auth-only placeholder
- `create_note(data, token, breadcrumb)` — encodes `ID_PROPERTIES` (`_id`, `resource_id`, `profile_id`), sets `created`/`saved` breadcrumbs
- `get_notes_for_resource(resource_id, token, breadcrumb)` — `MongoIO.get_documents` with `match={"resource_id": ObjectId}`, sorted by `created.at_time` descending

**Import changes**: Replace any `from api_utils...` imports as-is; no `src.services` imports exist in this file.

## Goals

- `api_utils.services.note_service.NoteService` matches mentee API behavior (create + read-by-resource).
- All MongoDB I/O uses `MongoIO.get_documents` / `create_document`.
- Unit tests ported to `tests/services/test_note_service.py` with `@patch` targets updated to `api_utils.services.note_service.*`.
- `api_utils/services/__init__.py` exports `NoteService`.

## Testing Expectations

- `pipenv run test tests/services/test_note_service.py` — all NoteService tests pass.
- `pipenv run test` — full suite passes (mock-based service tests do not require MongoDB).
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/note_service.py` — harvested `NoteService`
- `api_utils/services/__init__.py` — export `NoteService`
- `tests/services/__init__.py` — test package init (if needed)
- `tests/services/test_note_service.py` — ported unit tests

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
