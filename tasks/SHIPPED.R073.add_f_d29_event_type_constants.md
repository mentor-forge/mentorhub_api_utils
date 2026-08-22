# R073 – Add F-D29 event type constants

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R068_config_constants_pattern_and_drop_legacy_collections`  
**Description**: Extend Config event-type constants for Admin ingress, subscription lifecycle, invites, notifications, and GDPR event types added in F-D29 (T220).

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md` — fetch enumerators from running configurator
- `tasks/PENDING.R068.config_constants_pattern_and_drop_legacy_collections.md`
- `api_utils/config/config.py`
- `tests/config/test_config_constants.py`
- `../mentorhub_mongodb_api/configurator/enumerators/enumerations.0.yaml` — `event_types` block (planning snapshot)
- `../mentorhub/Workshops/customer_journey_issues_adjustments.md` — illustrative new types
- [F-D29](https://github.com/mentor-forge/mentorhub_mongodb_api/issues/61)

### Source of truth at execution

F-D29 enumerator work has shipped in `mentorhub_mongodb_api` (T220). Constant **values** must still exactly mirror the **running configurator** `event_types` strings (same rule as SHIPPED.R020). If the configurator is down, set **Status** to `Blocked` and stop.

```bash
pipenv run db
curl -s "http://localhost:8383/api/configurations/json_schema/Event.yaml/latest/" -H "accept: application/json"
# and/or enumerators endpoint for event_types
```

Constant **names** follow `EVENT_TYPE_<VALUE>` upper-snake convention.

Use inline constants pattern from R068 — not `config_strings`.

### New constants (planning snapshot from `enumerations.0.yaml`)

Retain existing mentee/mentor activity types. Add:

| Constant | Value (exact) |
| --- | --- |
| `EVENT_TYPE_EXTERNAL_RECEIVED` | `external_received` |
| `EVENT_TYPE_IDENTITY_PROVISIONED` | `identity_provisioned` |
| `EVENT_TYPE_ORGANIZATION_ENRICHED` | `organization_enriched` |
| `EVENT_TYPE_SUBSCRIPTION_CHANGED` | `subscription_changed` |
| `EVENT_TYPE_INVITE_CREATED` | `invite_created` |
| `EVENT_TYPE_INVITE_ACCEPTED` | `invite_accepted` |
| `EVENT_TYPE_NOTIFICATION_CREATED` | `notification_created` |
| `EVENT_TYPE_NOTIFICATION_DISMISSED` | `notification_dismissed` |
| `EVENT_TYPE_PAYMENT_RECORDED` | `payment_recorded` |
| `EVENT_TYPE_PROFILE_REDACTED` | `profile_redacted` |

Do **not** add collection-name constants here. Do **not** add `external_event_source` (`stripe` / `cognito`) as `EVENT_TYPE_*` values — that enumerator is not an event type.

## Goals

- All new F-D29 `event_types` values have matching `EVENT_TYPE_*` inline constants in `Config`.
- `tests/config/test_config_constants.py` asserts each new constant.
- Existing mentee/mentor event types unchanged.

## Testing Expectations

- `pipenv run test tests/config/`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/config/config.py`
- `tests/config/test_config_constants.py`

The agent must not update files outside this list.

## Execution Notes

**Plan:** Fetch live `event_types` from the running configurator Event JSON schema; add the 10 F-D29 values as inline `EVENT_TYPE_*` constants on `Config` (R068 pattern, not `config_strings`); retain existing mentee/mentor activity types; extend `test_config_constants.py` for value / not-in-config_strings / survive-initialize.

**Live enumerator values (source of truth):** After `pipenv run db`, `GET http://localhost:8383/api/configurations/json_schema/Event.yaml/latest/` returned `type.enum` (sorted):

`advanced`, `arrived`, `completed`, `encounter`, `external_received`, `fail`, `identity_provisioned`, `invite_accepted`, `invite_created`, `link`, `login`, `logout`, `note`, `notification_created`, `notification_dismissed`, `organization_enriched`, `payment_recorded`, `profile_redacted`, `started`, `subscription_changed`.

Existing constants already cover the 10 activity types. Added the 10 new values (exact strings). Did **not** add `stripe` / `cognito` (`external_event_source`, not `event_types`).

**Commands run:**
- `pipenv run db` — started mongodb + configurator
- `curl` Event.yaml latest JSON schema (HTTP 200)
- `pipenv run test tests/config/` — Pipfile ignores extra path; ran full unit suite
- `pipenv run test`
- `pipenv run lint` — failed on 25 **pre-existing** files (not this task)
- `pipenv run black --check api_utils/config/config.py tests/config/test_config_constants.py` — both unchanged
- `pipenv run build` — `api_utils-0.6.0` sdist + wheel

**Test results:**
- `pipenv run test tests/config/` and `pipenv run test`: 269 passed, 24 deselected, 15 warnings
- Lint: repo-wide black would reformat 25 pre-existing files; changed files pass `black --check`
- Build: success (`api_utils-0.6.0.tar.gz`, `api_utils-0.6.0-py3-none-any.whl`)

**Follow-ups:** Orchestrator confirmation: `pipenv run test` 269 passed, build success. Status set to Shipped.
