# R057 – Unit tests for Resource multi-field list filters

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R056_extend_resource_list_filters`  
**Description**: Add unit tests covering the new Resource list filters (`url`, `interests`, `technologies`, `skill_level`): empty/omitted, match clauses, no-clause when blank, and combined AND with existing filters.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/services/resource_service.py` — `RESOURCE_LIST_FILTERS` after R056
- `api_utils/mongo_utils/list_query.py` — `parse_filter_params`, `build_match_filter`
- `tests/mongo_utils/test_list_query.py` — existing filter parse/match patterns
- `tests/services/test_resource_service.py` — `test_get_resources_applies_filters`
- `tests/flask_utils/test_list_request.py` — optional fixture alignment if it duplicates filter specs
- `tasks/PENDING.R056.extend_resource_list_filters.md` — filter contract

Prefer importing the real `RESOURCE_LIST_FILTERS` from `api_utils.services.resource_service` for new coverage so tests track the service constant (local fixture copies in existing tests may remain for generic `list_query` behavior).

## Goals

- Tests cover each new filter param:
  - **Empty / omitted** — blank or missing query values produce no match clause for that field.
  - **Match** — `contains` (`url`) builds case-insensitive `$regex`; `in_list` (`interests`, `technologies`, `skill_level`) builds `$in` with comma-split values.
  - **No-match shape** — parsed/blank inputs that should not appear in the match document (e.g. empty string, whitespace-only `in_list`) are omitted.
  - **Combined** — multiple new filters plus at least one existing filter (`name` / `description` / `status`) AND into a single match document (all clauses present; no OR-across-fields).
- `ResourceService.get_resources` test(s) assert the new filter values are merged into the `match` passed to `execute_list_query`.
- Existing pagination / order / archived-RBAC tests remain unchanged and green.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- **Unit tests**
  - `pipenv run test tests/mongo_utils/test_list_query.py`
  - `pipenv run test tests/services/test_resource_service.py`
  - `pipenv run test tests/flask_utils/test_list_request.py` — if that file’s fixtures/assertions were updated
  - `pipenv run test`
- **Lint / build**
  - `pipenv run lint`
  - `pipenv run build`

## Outputs

- `tests/mongo_utils/test_list_query.py` — cases for new Resource filter params (parse + `build_match_filter`), including combined AND
- `tests/services/test_resource_service.py` — extend or add `get_resources` filter assertions for the new params
- `tests/flask_utils/test_list_request.py` — only if needed to keep local filter fixtures consistent or to cover parse via `parse_list_request` with the real/extended spec

The agent must not update files outside this list.

## Execution Notes

**Plan**: Add unit coverage that imports real `RESOURCE_LIST_FILTERS` from `resource_service` for empty/omitted, contains/`in_list` match clauses, whitespace blank omission, and combined AND with existing filters; assert `get_resources` merges new params into `execute_list_query` match; add `parse_list_request` coverage via the real service filter/order specs. Leave production filter code unchanged.

**Changes**:
- `tests/mongo_utils/test_list_query.py` — `TestResourceMultiFieldFilters` (5 cases) importing service `RESOURCE_LIST_FILTERS`
- `tests/services/test_resource_service.py` — `test_get_resources_applies_multi_field_filters`
- `tests/flask_utils/test_list_request.py` — `test_parse_list_request_resource_multi_field_filters` using real service specs

**Test results**:
- `pipenv run test tests/mongo_utils/test_list_query.py` — 184 passed, 6 deselected (script runs full suite)
- `pipenv run test tests/services/test_resource_service.py` — 184 passed, 6 deselected
- `pipenv run test tests/flask_utils/test_list_request.py` — 184 passed, 6 deselected
- `pipenv run test` — 184 passed, 6 deselected
- `pipenv run black --check` on the three output test files — unchanged (clean)
- `pipenv run lint` — fails repo-wide (26 unrelated files would be reformatted; R057 output files clean; pre-existing)
- `pipenv run build` — succeeded (`api_utils-0.5.0` sdist + wheel)

**Out of scope (deferred)**: R058 version bump.
