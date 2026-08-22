# R068 – Config constants pattern and drop legacy collections

**Status**: Pending  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Refactor `Config` so collection names, role strings, and event-type strings are **constants** initialized at declaration (not loaded via `config_strings` / `initialize()`). Remove collection-name constants for collections that are no longer persisted Mongo dictionaries. Delete orphaned config test-data files. Prerequisite for F-UA08 / Admin and Discovery API bootstrap.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R010.add_resource_aggregation_collection_config.md` — prior collection-name pattern (superseded)
- `tasks/SHIPPED.R020.add_event_type_constants_config.md` — prior event-type pattern (superseded)
- `api_utils/config/config.py`
- `tests/config/test_config_defaults.py`
- `tests/config/test_config_env.py`
- `tests/config/test_config_file.py`
- `tests/test_data/config/`
- `../mentorhub_mongodb_api/configurator/configurations/` — **authoritative persisted collection names** (`file_name` without `.yaml`; version `0.1.0.0` only)
- `../mentorhub/Workshops/customer_journey_issues.md` — E0 drops
- `../mentorhub/Workshops/customer_journey_issues_adjustments.md` — F-UA08 prerequisite
- [F-UA08](https://github.com/mentor-forge/mentorhub_api_utils/issues/17)

### Dropped collection-name constants (remove from Config)

These keys exist in `config.py` today but are **not** persisted Mongo collections in `mentorhub_mongodb_api`. Delete the constants and any references:

| Constant (remove) | Configurator status |
| --- | --- |
| `IDENTITY_COLLECTION_NAME` | Identity dictionary/configuration removed (T200). Profile is the canonical person document. |
| `LOGIN_COLLECTION_NAME` | No Login dictionary or configuration exists. |
| `SUBSCRIPTION_COLLECTION_NAME` | Top-level Subscription removed (T218 / F-D14). Billing lives on `Customer.subscriptions[]`. |
| `DASHBOARD_COLLECTION_NAME` | Dashboard dictionary/configuration removed (T219 / F-D15). |
| `CARD_COLLECTION_NAME` | Card is a **configurator-only** schema at version `0.0.0.0` (T223) — it does **not** create a Mongo collection. Payment Card was already dropped (F-D16). |

No `CardService`, `DashboardService`, `SubscriptionService`, `IdentityService`, or `LoginService` exist in `api_utils/services/` — nothing to delete there.

Do **not** add a `CARD_COLLECTION_NAME` for the Discovery Card schema.

### Retained data collection names (this task)

Keep these constants. Values must match configurator `file_name` (without `.yaml`) exactly:

| Constant | Value |
| --- | --- |
| `PROFILE_COLLECTION_NAME` | `Profile` |
| `CUSTOMER_COLLECTION_NAME` | `Customer` |
| `EVENT_COLLECTION_NAME` | `Event` |
| `RESOURCE_COLLECTION_NAME` | `Resource` |
| `RESOURCE_AGGREGATION_COLLECTION_NAME` | `Resource_Aggregation` |
| `PATH_COLLECTION_NAME` | `Path` |
| `PLAN_COLLECTION_NAME` | `Plan` |
| `ENCOUNTER_COLLECTION_NAME` | `Encounter` |
| `JOURNEY_COLLECTION_NAME` | `Journey` |
| `MENTEE_COLLECTION_NAME` | `Mentee` |
| `RATING_COLLECTION_NAME` | `Rating` |
| `NOTE_COLLECTION_NAME` | `Note` |

System collection names (`ENUMERATORS_COLLECTION_NAME` = `DatabaseEnumerators`, `VERSIONS_COLLECTION_NAME` = `CollectionVersions`) stay as constants with the same values.

New persisted collections **Setting**, **Payment**, **ExternalEvent**, and **Notification** are added in R069 — do **not** add them here.

### Constants pattern (target)

Move **retained** collection names, all `ROLE_*`, and all `EVENT_TYPE_*` out of `config_strings` and the empty `self.X = ''` prelude. Assign values inline in `__init__` immediately after `config_items` / `versions` / `enumerators` setup:

```python
# Data collection names (MongoDB dictionary names)
self.PROFILE_COLLECTION_NAME = "Profile"
self.CUSTOMER_COLLECTION_NAME = "Customer"
# ...
```

One single-line comment per group (`# System collection names`, `# Data collection names`, `# Role constants`, `# Event type constants`). No extra feature documentation.

Constants are **not** overridable via env var or `CONFIG_FOLDER` file — remove their entries from `config_strings` and delete matching files under `tests/test_data/config/`.

Configurable settings (ports, secrets, folders, `MONGO_DB_NAME`, etc.) stay in `config_strings` / `config_ints` / secrets dicts unchanged.

## Goals

- Retained `*_COLLECTION_NAME`, `ROLE_*`, and `EVENT_TYPE_*` values are assigned inline in `Config.__init__`; removed from `config_strings` and from the `initialize()` string loop.
- `IDENTITY_COLLECTION_NAME`, `LOGIN_COLLECTION_NAME`, `CARD_COLLECTION_NAME`, `DASHBOARD_COLLECTION_NAME`, and `SUBSCRIPTION_COLLECTION_NAME` are removed from `config.py` (declarations and defaults).
- Orphaned test-data files deleted for every key removed from `config_strings` (all former constant keys plus the five dropped collection names).
- New `tests/config/test_config_constants.py` asserts retained constant values directly (defaults match dictionary / enumerator names; event types mirror `event_types` in enumerations).
- Existing config tests (`test_config_defaults`, `test_config_env`, `test_config_file`) still pass for remaining configurable keys only.
- Services continue to read constants via `Config.get_instance().<NAME>` — no service behavior change required for this task.

## Testing Expectations

Run from the api_utils repository root:

- `pipenv run test tests/config/`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/config/config.py` — constants pattern; drop Identity/Login/Card/Dashboard/Subscription
- `tests/config/test_config_constants.py` — new constants assertions
- `tests/config/test_config_defaults.py` — adjust if needed (constants no longer in `config_strings`)
- `tests/config/test_config_env.py` — adjust if needed
- `tests/config/test_config_file.py` — adjust if needed
- `tests/test_data/config/` — delete orphaned files (see list below; agent may delete only files that exist)

Files to delete under `tests/test_data/config/` when present:

- `IDENTITY_COLLECTION_NAME`, `LOGIN_COLLECTION_NAME`, `CARD_COLLECTION_NAME`, `DASHBOARD_COLLECTION_NAME`, `SUBSCRIPTION_COLLECTION_NAME`
- Every retained constant key moved out of `config_strings`: all other `*_COLLECTION_NAME`, all `ROLE_*`, all `EVENT_TYPE_*`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
