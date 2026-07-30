# R069 – Add ExternalEvent and Notification collection constants

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R068_config_constants_pattern_and_drop_legacy_collections`  
**Description**: Add Config constants for new cross-domain MongoDB dictionaries introduced in F-D29 (Admin ingress + Discovery). Uses the inline constants pattern from R068.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/PENDING.R068.config_constants_pattern_and_drop_legacy_collections.md`
- `api_utils/config/config.py`
- `tests/config/test_config_constants.py` (created in R068)
- `../mentorhub/Workshops/customer_journey_issues.md` — schema snapshot (ExternalEvent, Notification)
- `../mentorhub/Workshops/customer_journey_issues_adjustments.md` — F-D29 / F-UA08
- `../mentorhub/Workshops/admin_journey_issues.md` — ingress collections
- `../mentorhub/Workshops/discovery_journey_issues.md` — Notification dismiss ownership
- [F-D29](https://github.com/mentor-forge/mentorhub_mongodb_api/issues/61) — dictionary schemas (external; confirm names via configurator when available)

### New collection constants

| Constant | Value | Dictionary |
| --- | --- | --- |
| `EXTERNAL_EVENT_COLLECTION_NAME` | `ExternalEvent` | Append-only ingress record (F-AA02) |
| `NOTIFICATION_COLLECTION_NAME` | `Notification` | Scoped notification docs (Discovery read/dismiss) |

Place in the `# Data collection names` group in `config.py`. Do **not** add to `config_strings` or create `tests/test_data/config/` files (constants are not overridable).

Product, Payment, and Discount dictionaries are F-D22 scope — **out of scope** for this task.

## Goals

- `EXTERNAL_EVENT_COLLECTION_NAME` and `NOTIFICATION_COLLECTION_NAME` declared inline in `Config.__init__` with values above.
- `tests/config/test_config_constants.py` extended to assert both names.
- No env/file override plumbing for these keys.

## Testing Expectations

- `pipenv run test tests/config/`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/config/config.py` — add two collection constants
- `tests/config/test_config_constants.py` — assert new constants

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
