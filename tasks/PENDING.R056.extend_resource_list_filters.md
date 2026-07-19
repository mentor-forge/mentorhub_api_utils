# R056 – Extend Resource list filters (url, interests, technologies, skill_level)

**Status**: Pending  
**Type**: Feature  
**Depends On**: none  
**Description**: Extend `RESOURCE_LIST_FILTERS` so Resource list endpoints can filter by `url`, `interests`, `technologies`, and `skill_level` using existing `contains` / `in_list` types, without changing pagination, order, or AND composition.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/services/resource_service.py` — current `RESOURCE_LIST_FILTERS` / `RESOURCE_LIST_ORDER` and `get_resources`
- `api_utils/mongo_utils/list_query.py` — `parse_filter_params`, `build_match_filter` (`contains` / `in_list`)
- `tasks/SHIPPED.R050.refactor_resource_service_list.md` — how list filters were introduced
- `../mentorhub_mentee_api/tasks/ISSUE.mentorhub_api_utils.extend_resource_list_filters.md` — consumer request / contract

### Current contract (`0.5.0`)

```python
RESOURCE_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "description": {"type": "contains", "field": "description"},
    "status": {"type": "in_list", "field": "status"},
}
```

### Target additions (patch)

| Query param | Type | Match behavior |
|-------------|------|----------------|
| `url` | `contains` | Case-insensitive substring on `url` |
| `interests` | `in_list` | Comma-separated values → Mongo `$in` on `interests` (array field — any element in list) |
| `technologies` | `in_list` | Comma-separated values → Mongo `$in` on `technologies` |
| `skill_level` | `in_list` | Comma-separated values → Mongo `$in` on scalar `skill_level` |

**Constraints**

- Keep `name` / `description` / `status` entries and `RESOURCE_LIST_ORDER` unchanged.
- Do not add a new filter type — existing `contains` / `in_list` in `list_query.py` are sufficient (including array `$in` semantics).
- Do not introduce OR-across-fields or a single `q` param; `build_match_filter` must continue ANDing all provided filters.
- Field names are **`technologies`** (plural) and **`skill_level`**.
- Out of scope: Resource document shape, enumerator values, mentee OpenAPI/docs, SPA UI, version bump (R058).

## Goals

- `RESOURCE_LIST_FILTERS` in `api_utils/services/resource_service.py` includes the four new entries above alongside the existing three.
- `ResourceService.get_resources` continues to call `build_match_filter(..., RESOURCE_LIST_FILTERS)` so new filters participate in the same AND match composition with no service signature changes.
- No changes to `list_query.py` filter types, pagination, or order-by behavior.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- **Unit tests**
  - `pipenv run test tests/services/test_resource_service.py`
  - `pipenv run test tests/mongo_utils/test_list_query.py`
  - `pipenv run test` — full suite still green (new filter coverage is R057)
- **Lint / build**
  - `pipenv run lint`
  - `pipenv run build`

## Outputs

- `api_utils/services/resource_service.py` — extend `RESOURCE_LIST_FILTERS` only (do not change `RESOURCE_LIST_ORDER` or method signatures unless required for correctness)

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
