# R052 – Add standardized Get List to NoteService.get_notes_for_resource

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Paginate `NoteService.get_notes_for_resource` within the resource scope and support optional `status` in_list filtering.

## Execution Notes

- Paginated `get_notes_for_resource` with `NOTE_LIST_FILTERS`/`NOTE_LIST_ORDER`.
- Added `list_all_notes_for_resource` for composite reads; aggregation and resource detail use it.
- Updated note, aggregation, and resource service tests.
- `pipenv run test`: 177 passed, 6 deselected.
