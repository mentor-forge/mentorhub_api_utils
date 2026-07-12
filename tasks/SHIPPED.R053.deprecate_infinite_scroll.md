# R053 – Deprecate execute_infinite_scroll_query

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R055_add_event_service_list`  
**Description**: Mark `execute_infinite_scroll_query` as deprecated, document the replacement Get List pattern in README, and retain tests until downstream APIs migrate off infinite scroll.

## Execution Notes

- Added deprecation notices to `infinite_scroll.py`.
- Documented Get List pattern in README; module and tests retained for migration window.
- `pipenv run test`: 177 passed, 6 deselected.
