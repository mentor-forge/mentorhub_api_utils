# R069 – Add ExternalEvent, Notification, Setting, and Payment collection constants

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R068_config_constants_pattern_and_drop_legacy_collections`  
**Description**: Add Config constants for persisted MongoDB dictionaries that are missing from Config after R068: F-D29 ingress/Discovery collections and F-D22 commerce collections. Uses the inline constants pattern from R068.

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
- `../mentorhub_mongodb_api/configurator/configurations/ExternalEvent.yaml`
- `../mentorhub_mongodb_api/configurator/configurations/Notification.yaml`
- `../mentorhub_mongodb_api/configurator/configurations/Setting.yaml`
- `../mentorhub_mongodb_api/configurator/configurations/Payment.yaml`
- `../mentorhub/Workshops/customer_journey_issues.md` — schema snapshot
- `../mentorhub/Workshops/customer_journey_issues_adjustments.md` — F-D29 / F-UA08
- `../mentorhub/Workshops/admin_journey_issues.md` — ingress collections
- `../mentorhub/Workshops/discovery_journey_issues.md` — Notification dismiss ownership
- [F-D29](https://github.com/mentor-forge/mentorhub_mongodb_api/issues/61)
- [F-D22](https://github.com/mentor-forge/mentorhub_mongodb_api/issues/50)

### New collection constants

Place in the `# Data collection names` group in `config.py`. Values must match configurator `file_name` (without `.yaml`) exactly. Do **not** add to `config_strings` or create `tests/test_data/config/` files (constants are not overridable).

| Constant | Value | Dictionary |
| --- | --- | --- |
| `EXTERNAL_EVENT_COLLECTION_NAME` | `ExternalEvent` | Append-only ingress record (F-AA02 / T221) |
| `NOTIFICATION_COLLECTION_NAME` | `Notification` | Scoped notification docs (Discovery read/dismiss / T222) |
| `SETTING_COLLECTION_NAME` | `Setting` | Polymorphic Admin/reference bag — Product and Discount **variants** (T227) |
| `PAYMENT_COLLECTION_NAME` | `Payment` | Stripe-backed payment records (T229) |

### Not collection names

Do **not** add `PRODUCT_COLLECTION_NAME` or `DISCOUNT_COLLECTION_NAME`. Product and Discount are `type` discriminators on **Setting** (`type: Product` / `type: Discount`), not Mongo collections.

Do **not** add `CARD_COLLECTION_NAME`. Card is configurator-only at version `0.0.0.0` and does not create a collection (R068 already dropped it).

## Goals

- The four constants above are declared inline in `Config.__init__` with the values in the table.
- `tests/config/test_config_constants.py` extended to assert all four names.
- No env/file override plumbing for these keys.
- No Product/Discount/Card collection-name constants.

## Testing Expectations

- `pipenv run test tests/config/`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/config/config.py` — add four collection constants
- `tests/config/test_config_constants.py` — assert new constants

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
