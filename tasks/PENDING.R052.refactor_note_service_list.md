# R052 – Add standardized Get List to NoteService.get_notes_for_resource

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Paginate `NoteService.get_notes_for_resource` within the resource scope and support optional `status` in_list filtering.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/list_query.py` — R049 utilities
- `api_utils/services/note_service.py` — `get_notes_for_resource` returns all notes for a resource
- `api_utils/services/aggregation_service.py` — `get_aggregation_detail` embeds full note list via `get_notes_for_resource`
- `api_utils/services/resource_service.py` — `get_resource` composite also embeds notes
- `tests/services/test_note_service.py`

**Breaking change**: Default pagination (`size=20`) reduces notes returned in aggregation/resource composites unless callers pass an explicit larger `size` or a documented `size=None` “no limit” escape hatch for composite reads. Prefer: composite methods pass `offset=0, size=MAX_SIZE` (or dedicated internal helper) so public list endpoints paginate while composites retain full lists until downstream OpenAPI splits notes out.

## Goals

- `NoteService.get_notes_for_resource(resource_id, token, breadcrumb, offset=DEFAULT_OFFSET, size=DEFAULT_SIZE, filters=None, sort_by=None)`:
  - Base `match`: `{"resource_id": ObjectId(resource_id)}`
  - `NOTE_LIST_ORDER` default `created.at_time` desc; allowed: `created.at_time` (`asc`/`desc`)
  - Optional `status` in_list filter
  - Uses `execute_list_query`
- `AggregationService.get_aggregation_detail` and `ResourceService.get_resource` updated to request full note sets for composites (explicit `size=MAX_SIZE` and default sort, or internal `_list_all_notes_for_resource` — document choice in Execution Notes)
- Unit tests for pagination, status filter, and composite callers still receiving expected note counts in mocks

## Testing Expectations

- `pipenv run test tests/services/test_note_service.py`
- `pipenv run test tests/services/test_aggregation_service.py`
- `pipenv run test tests/services/test_resource_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/note_service.py`
- `api_utils/services/aggregation_service.py` — composite note fetch adjustment
- `api_utils/services/resource_service.py` — composite note fetch adjustment
- `tests/services/test_note_service.py`
- `tests/services/test_aggregation_service.py`
- `tests/services/test_resource_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
