# R055 – Add standardized Get List to EventService

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Add `EventService.get_events` using the shared list-query utilities (offset/size pagination, `type` in_list filter, optional profile scope) so mentor API can drop local infinite-scroll list logic.

## Execution Notes

- Added `get_events` with `EVENT_LIST_FILTERS`, `EVENT_LIST_ORDER`, and optional `profile_id` scope.
- Added unit tests for list, profile scope, and type filter.
- `pipenv run test`: 177 passed, 6 deselected.
