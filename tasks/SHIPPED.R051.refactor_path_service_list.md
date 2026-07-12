# R051 – Add standardized Get List to PathService.get_paths

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Extend `PathService.get_paths` with offset/size pagination and optional `name` contains filter, using the shared list-query utilities.

## Execution Notes

- Added paginated `get_paths` with `PATH_LIST_FILTERS` and `PATH_LIST_ORDER`.
- Updated path service tests to mock `execute_list_query`.
- `pipenv run test`: 177 passed, 6 deselected.
