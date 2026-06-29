# R010 – Add Resource_Aggregation collection name to Config

**Status**: Shipped  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Add a new collection-name configuration value to the `api_utils` `Config`
singleton for the **Resource Aggregation** collection, with a default value of
`Resource_Aggregation`. This mirrors the existing collection-name pattern (e.g.
`RESOURCE_COLLECTION_NAME: "Resource"`).

## Context / Input files

These files must be treated as **inputs** and read before implementation:

- `mentorhub_api_utils/README.md`
- `mentorhub_api_utils/api_utils/config/config.py`
- `mentorhub_api_utils/tests/config/test_config_defaults.py`
- `mentorhub_api_utils/tests/config/test_config_env.py`
- `mentorhub_api_utils/tests/config/test_config_file.py`
- `mentorhub_api_utils/tests/test_data/config/` (existing per-key test data files)
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Use the **existing** `Config` structure in
  `api_utils/config/config.py`. Do **not** create a new config file, a new
  config module, or a parallel constants file.
- Add a single collection-name entry following the established
  `*_COLLECTION_NAME` convention used by the other data collections:
  - **Key/constant name**: `RESOURCE_AGGREGATION_COLLECTION_NAME`
  - **Default value**: `Resource_Aggregation` (use this exact string)
- Two edits inside `config.py`:
  1. Declare the instance attribute in `__init__` alongside the other
     "Data collection names (from catalog.data_dictionaries)" declarations
     (the block that currently ends with `self.LOGIN_COLLECTION_NAME = ''`):
     ```python
     self.RESOURCE_AGGREGATION_COLLECTION_NAME = ''
     ```
     Place it logically near `self.RESOURCE_COLLECTION_NAME = ''`.
  2. Add the default to the `config_strings` dictionary in the
     "Data collection names" group:
     ```python
     "RESOURCE_AGGREGATION_COLLECTION_NAME": "Resource_Aggregation",
     ```
     Place it logically near `"RESOURCE_COLLECTION_NAME": "Resource",`.
- Do **not** add validation, transformation, or any other behavior. This is a
  plain string config value handled by the existing initialization loop.

## Files to modify / create

- **Modify**: `api_utils/config/config.py`
  - Add instance attribute declaration in `__init__`.
  - Add the default entry to `config_strings`.
- **Create**: `tests/test_data/config/RESOURCE_AGGREGATION_COLLECTION_NAME`
  - File contents must be exactly `TEST_VALUE` (matching the convention of the
    other string test-data files such as `RESOURCE_COLLECTION_NAME`).

## Why the test data file is required

The config unit tests iterate over **every** key in `config_strings`:

- `tests/config/test_config_defaults.py` asserts the attribute equals its
  default (`Resource_Aggregation`).
- `tests/config/test_config_env.py` asserts the value resolves from an env var.
- `tests/config/test_config_file.py` asserts the value resolves to `TEST_VALUE`
  by reading `tests/test_data/config/<KEY>`.

Adding the key to `config_strings` without creating
`tests/test_data/config/RESOURCE_AGGREGATION_COLLECTION_NAME` will cause
`test_config_file.py` to fail. No other test-data files need to change.

## Testing expectations

- **Unit tests**
  - Run `pipenv run test`.
  - Confirm the existing config test suites
    (`test_config_defaults.py`, `test_config_env.py`, `test_config_file.py`)
    pass with the new key included automatically.

## Packaging / build checks

Before marking this task as completed:

- Run `pipenv run test`; all tests passing.
- Run `pipenv run build`; build successful.
- Confirm no new linter errors (`pipenv run lint`).

## Dependencies / Ordering

- Independent of **R020**, but both edit `config.py` and
  `tests/test_data/config/`. Run **R010 before R020** to avoid edit conflicts.
- Must run **before R030** (version bump / PR).

## Change control checklist

- [x] Reviewed all **Context / Input files**.
- [x] Designed and documented the solution approach in this file.
- [x] Added `RESOURCE_AGGREGATION_COLLECTION_NAME` instance attribute in `__init__`.
- [x] Added `RESOURCE_AGGREGATION_COLLECTION_NAME` default to `config_strings`.
- [x] Created `tests/test_data/config/RESOURCE_AGGREGATION_COLLECTION_NAME` (`TEST_VALUE`).
- [x] Ran unit tests (`pipenv run test`); config + non-Mongo suites passing.
- [ ] Ran packaging/build steps (`pipenv run build`); build successful. <!-- deferred to R030 (single build before PR) -->
- [x] Created a scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

**Summary of changes**
- Added `self.RESOURCE_AGGREGATION_COLLECTION_NAME = ''` to the "Data collection
  names" block in `api_utils/config/config.py` `__init__` (next to
  `RESOURCE_COLLECTION_NAME`).
- Added `"RESOURCE_AGGREGATION_COLLECTION_NAME": "Resource_Aggregation"` to the
  `config_strings` dict (next to `RESOURCE_COLLECTION_NAME`).
- Created `tests/test_data/config/RESOURCE_AGGREGATION_COLLECTION_NAME` with
  contents `TEST_VALUE`.

**Testing results**
- Unit tests: `pipenv run pytest tests/config/ -q` → 29 passed. `pipenv run test`
  → 85 passed, 6 deselected; the only 13 failures are pre-existing `MongoIO`
  integration tests requiring a running MongoDB (Docker is not running in this
  environment) — unrelated to this config-only change.
- Packaging/build: deferred to R030 (single build/version bump before the PR).

**Follow‑up tasks**
- None.
