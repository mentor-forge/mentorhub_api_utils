# R020 – Add Event Type constants to Config

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Add constants to the `api_utils` `Config` singleton that represent the
**Event Type** values defined under `event_types` in the MongoDB configurator
enumerations. These constants give APIs a single, shared source for event-type
string values, following the same pattern already used for the `ROLE_*`
constants (e.g. `ROLE_MENTOR: "mentor"`).

## Source of truth (do not rename or transform)

Values come from `event_types` in
`mentorhub_mongodb_api/configurator/enumerators/enumerations.0.yaml`. The
constant **values must exactly mirror** these strings — no renaming, casing
changes, or other transformation:

| Constant name              | Value (exact)  |
| -------------------------- | -------------- |
| `EVENT_TYPE_LOGIN`         | `login`        |
| `EVENT_TYPE_LOGOUT`        | `logout`       |
| `EVENT_TYPE_FAIL`          | `fail`         |
| `EVENT_TYPE_ARRIVED`       | `arrived`      |
| `EVENT_TYPE_COMPLETED`     | `completed`    |
| `EVENT_TYPE_STARTED`       | `started`      |
| `EVENT_TYPE_ENCOUNTER`     | `encounter`    |
| `EVENT_TYPE_NOTE`          | `note`         |
| `EVENT_TYPE_LINK`          | `link`         |
| `EVENT_TYPE_ADVANCED`      | `advanced`     |

> Note: the constant **names** follow the existing `Config` naming convention
> (UPPER_SNAKE, prefixed `EVENT_TYPE_`), exactly as the `ROLE_*` constants
> prefix the `user_roles` enum values. Only the **values** mirror the YAML.

## Context / Input files

These files must be treated as **inputs** and read before implementation:

- `mentorhub_mongodb_api/configurator/enumerators/enumerations.0.yaml` (the `event_types` block)
- `mentorhub_api_utils/README.md`
- `mentorhub_api_utils/api_utils/config/config.py`
- `mentorhub_api_utils/tests/config/test_config_defaults.py`
- `mentorhub_api_utils/tests/config/test_config_env.py`
- `mentorhub_api_utils/tests/config/test_config_file.py`
- `mentorhub_api_utils/tests/test_data/config/` (existing per-key test data files)
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- First **check whether Event Type constants already exist** in `config.py`.
  As of this task's authoring they do **not** (only `ROLE_*` constants exist).
  - If they are **absent**: add them as described below.
  - If they are **present** (added by a prior task): **extend/update** the
    existing block to cover any missing `event_types` values rather than
    duplicating definitions. Do not introduce a second event-type structure.
- Use the **existing** `Config` structure. Do **not** create a new config file,
  a new module, an Enum class, or a parallel constants file. These are plain
  string config values handled by the existing initialization loop.
- Two edits inside `config.py`:
  1. Add a new "Event Type Constants" group of instance-attribute declarations
     in `__init__`, immediately after the `# Role Constants` block:
     ```python
     # Event Type Constants
     self.EVENT_TYPE_LOGIN = ''
     self.EVENT_TYPE_LOGOUT = ''
     self.EVENT_TYPE_FAIL = ''
     self.EVENT_TYPE_ARRIVED = ''
     self.EVENT_TYPE_COMPLETED = ''
     self.EVENT_TYPE_STARTED = ''
     self.EVENT_TYPE_ENCOUNTER = ''
     self.EVENT_TYPE_NOTE = ''
     self.EVENT_TYPE_LINK = ''
     self.EVENT_TYPE_ADVANCED = ''
     ```
  2. Add the defaults to the `config_strings` dictionary, in a new
     "Event Type Constants" group placed after the `# Role Constants` entries:
     ```python
     # Event Type Constants
     "EVENT_TYPE_LOGIN": "login",
     "EVENT_TYPE_LOGOUT": "logout",
     "EVENT_TYPE_FAIL": "fail",
     "EVENT_TYPE_ARRIVED": "arrived",
     "EVENT_TYPE_COMPLETED": "completed",
     "EVENT_TYPE_STARTED": "started",
     "EVENT_TYPE_ENCOUNTER": "encounter",
     "EVENT_TYPE_NOTE": "note",
     "EVENT_TYPE_LINK": "link",
     "EVENT_TYPE_ADVANCED": "advanced",
     ```
- Keep responsibilities in the config layer only. Do **not** add lookup
  helpers, validation against the enumerators, or route/service logic.

## Files to modify / create

- **Modify**: `api_utils/config/config.py`
  - Add the 10 `EVENT_TYPE_*` instance attribute declarations in `__init__`.
  - Add the 10 `EVENT_TYPE_*` default entries to `config_strings`.
- **Create** (one file per constant, contents exactly `TEST_VALUE`) under
  `tests/test_data/config/`:
  - `EVENT_TYPE_LOGIN`
  - `EVENT_TYPE_LOGOUT`
  - `EVENT_TYPE_FAIL`
  - `EVENT_TYPE_ARRIVED`
  - `EVENT_TYPE_COMPLETED`
  - `EVENT_TYPE_STARTED`
  - `EVENT_TYPE_ENCOUNTER`
  - `EVENT_TYPE_NOTE`
  - `EVENT_TYPE_LINK`
  - `EVENT_TYPE_ADVANCED`

## Why the test data files are required

The config unit tests iterate over **every** key in `config_strings`:

- `tests/config/test_config_defaults.py` asserts each attribute equals its
  default (the exact YAML value).
- `tests/config/test_config_env.py` asserts each value resolves from an env var.
- `tests/config/test_config_file.py` asserts each value resolves to
  `TEST_VALUE` by reading `tests/test_data/config/<KEY>`.

Adding the keys to `config_strings` without creating the matching
`tests/test_data/config/EVENT_TYPE_*` files will cause `test_config_file.py`
to fail. No edits to existing test-data files are needed.

## Testing expectations

- **Unit tests**
  - Run `pipenv run test`.
  - Confirm the config test suites pick up all 10 new keys and pass
    (defaults equal the exact YAML values; file values equal `TEST_VALUE`).
  - Optionally verify the values still match the `event_types` block in
    `enumerations.0.yaml` (manual cross-check; no automated coupling required).

## Packaging / build checks

Before marking this task as completed:

- Run `pipenv run test`; all tests passing.
- Run `pipenv run build`; build successful.
- Confirm no new linter errors (`pipenv run lint`).

## Dependencies / Ordering

- Both **R010** and **R020** edit `config.py` and `tests/test_data/config/`.
  Run **after R010** to avoid edit conflicts.
- Must run **before R030** (version bump / PR).

## Change control checklist

- [ ] Reviewed all **Context / Input files**, including the `event_types` block.
- [ ] Confirmed whether event-type constants already exist; extended vs. added accordingly.
- [ ] Added the 10 `EVENT_TYPE_*` instance attributes in `__init__`.
- [ ] Added the 10 `EVENT_TYPE_*` defaults to `config_strings` with exact YAML values.
- [ ] Created the 10 `tests/test_data/config/EVENT_TYPE_*` files (`TEST_VALUE`).
- [ ] Verified values exactly mirror `enumerations.0.yaml` (no renaming/transformation).
- [ ] Ran unit tests (`pipenv run test`); all passing.
- [ ] Ran packaging/build steps (`pipenv run build`); build successful.
- [ ] Created a scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

**Summary of changes**
- _e.g., "Added EVENT_TYPE_* constants to config.py and their test data files."_

**Testing results**
- Unit tests: _command(s) run, high‑level outcome_
- Packaging/build: _command(s) run, high‑level outcome_

**Follow‑up tasks**
- _none expected_
