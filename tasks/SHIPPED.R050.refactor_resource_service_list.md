# R050 – Refactor ResourceService.get_resources to standardized Get List

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R049_add_list_query_utilities`  
**Description**: Replace Python-side slicing in `ResourceService.get_resources` with `execute_list_query`, add extensible query filters (`name`, `description`, `status`), and remove duplicated pagination helpers.

## Execution Notes

- Refactored `get_resources` to use `execute_list_query`, `build_match_filter`, and `RESOURCE_LIST_FILTERS`/`RESOURCE_LIST_ORDER`.
- Added optional `filters` and `sort_by` kwargs; removed local `_validate_pagination`.
- `pipenv run test`: 177 passed, 6 deselected.
