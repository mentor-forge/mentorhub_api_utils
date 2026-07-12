# R044 – Harvest ResourceService into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R043_harvest_event_service`  
**Description**: Move `ResourceService` from `mentorhub_mentee_api` into `api_utils.services.resource_service` with unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

- Source: `../mentorhub_mentee_api/src/services/resource_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_resource_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `../mentorhub_mentee_api/src/services/resource_service.py`
- `../mentorhub_mentee_api/test/services/test_resource_service.py`
- `api_utils/services/aggregation_service.py`
- `api_utils/services/note_service.py`
- `api_utils/config/config.py` — `ROLE_ADMIN`, `RESOURCE_COLLECTION_NAME`

**ResourceService surface** (mentee API):

- `get_resources(token, breadcrumb, offset, size)` — fetches all via `MongoIO.get_documents`, slices in Python; non-admin excludes `status: archived`
- `get_resources_by_ids(resource_ids, token, breadcrumb)` — batch lookup with `match={"_id": {"$in": object_ids}}`, `project={"name": 1, "description": 1}`, archived filter for non-admin
- `get_resource(resource_id, token, breadcrumb)` — returns composite `{resource, aggregation, notes}` via `AggregationService.get_aggregation_for_resource` and `NoteService.get_notes_for_resource`
- Pagination constants: `DEFAULT_OFFSET=0`, `DEFAULT_SIZE=20`, `MAX_SIZE=100`
- `_is_admin`, `_validate_pagination`, `_to_resource_summary` helpers

**Import changes**:

- Replace `from src.services.aggregation_service import AggregationService` and `from src.services.note_service import NoteService` with `api_utils.services.*` imports (lazy inside `get_resource`).

**Note**: `mentorhub_mentor_api` uses infinite-scroll list pagination and CRUD operations. Downstream refactor will address mentor-specific extensions; harvest mentee read-focused implementation.

## Goals

- `api_utils.services.resource_service.ResourceService` matches mentee API behavior for list, batch-by-ids, and detail composite.
- All MongoDB reads use `MongoIO.get_documents` / `get_document` (no `collection.find`).
- Unit tests ported to `tests/services/test_resource_service.py`.
- `api_utils/services/__init__.py` exports `ResourceService`.

## Testing Expectations

- `pipenv run test tests/services/test_resource_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/resource_service.py`
- `api_utils/services/__init__.py` — export `ResourceService`
- `tests/services/test_resource_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
