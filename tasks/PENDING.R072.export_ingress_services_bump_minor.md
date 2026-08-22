# R072 – Export ingress services and bump minor version

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R070_scaffold_external_event_service`, `R071_scaffold_notification_service`  
**Description**: Export `ExternalEventService` and `NotificationService` from the public API, update README, and bump `pyproject.toml` minor version for the F-UA08 release.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R066.export_services_and_bump_minor.md` — prior export/bump pattern
- `pyproject.toml` — current version (expected `0.6.0` at planning time)
- `api_utils/services/__init__.py`

### Versioning

- **Minor** bump: additive Config constants refactor (including ExternalEvent, Notification, Setting, Payment), dropped legacy collection keys (Identity, Login, Card, Dashboard, Subscription), two new services — backward compatible for consumers that did not rely on the dropped config keys.
- Expected `0.6.0` → **`0.7.0`**. If another release landed first, increment current minor by one.

Publishing to CodeArtifact is after PR merge via `pipenv run tag-release` — not in this task.

## Goals

- `api_utils/services/__init__.py` exports `ExternalEventService` and `NotificationService` in `__all__`.
- `README.md` documents F-UA08 constants pattern briefly (one paragraph max) and lists new services; updates `api-utils==` pin example to the new version.
- `pyproject.toml` `version` bumped to next minor.

## Testing Expectations

- `pipenv run test`
- `pipenv run lint`
- `pipenv run build` — artifact reflects new version (e.g. `api_utils-0.7.0-...`)

## Outputs

- `api_utils/services/__init__.py`
- `pyproject.toml`
- `README.md`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
