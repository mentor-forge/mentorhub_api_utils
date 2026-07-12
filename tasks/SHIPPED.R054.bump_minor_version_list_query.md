# R054 – Bump api-utils minor version for Get List pattern

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R053_deprecate_infinite_scroll`  
**Description**: Bump `api-utils` to `0.5.0` (minor) reflecting new list-query utilities, MongoIO pagination, and service signature extensions.

## Execution Notes

- `pyproject.toml` version → `0.5.0`.
- README updated with Get List changelog reference and version pin example.
- `pipenv run test`: 177 passed, 6 deselected; `pipenv run build` clean.
