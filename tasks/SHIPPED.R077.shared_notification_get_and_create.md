# R077 – Shared Notification GET (RBAC) and global create

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R075_classmethod_and_data_boundary_contract`  
**Description**: Keep Notification create + list on the shared service (global immutable POST + consume). Move `dismiss_notification` to the Discovery API subclass (Discovery **controls** Notification).

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml` — Discovery **controls** Notification; every domain may create immutable Notification
- `README.md`
- `tasks/_PLANNING.md` — **MongoDB dictionary schemas**
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R071.scaffold_notification_service.md`
- `tasks/ISSUE.mentorhub_discovery_api.notification_control.md`
- `api_utils/services/notification_service.py`
- `api_utils/services/event_service.py` — global POST + list reference
- `tests/services/test_notification_service.py`

Confirm live Notification JSON/BSON schema from the configurator. If unavailable, set **Status** to `Blocked` and stop.

### Keep

- `create_notification` — global POST; no `saved`; stamp `created`; encode ids at MongoIO boundary
- `get_notifications` — offset/size list, default `created.at_time` desc

### Outbound RBAC

Do **not** invent a one-off `$or` list filter here. F-UA12 outbound composition (admin root, token `profile_id` / `customer_id` / `mentor_id` / `global`, `status != archived`, get-by-id post-fetch) lands in **R082**. `get_notifications` may keep an optional caller `match` kwarg AND-combined with an empty default until then.

### Remove from shared

- `dismiss_notification` — Discovery control mutation. Method body is already specified in `ISSUE.mentorhub_discovery_api.notification_control.md`; delete the shared method and its unit tests.

## Goals

- Shared NotificationService is create + list only (outbound RBAC in R082).
- Dismiss lives only in the Discovery ISSUE / future API subclass.
- Tests cover create, list, and the absence of dismiss on the shared class.

## Testing Expectations

- `pipenv run test tests/services/test_notification_service.py`
- `pipenv run test`
- `pipenv run lint` — R077 files `black`-clean
- `pipenv run build`

## Outputs

- `api_utils/services/notification_service.py`
- `tests/services/test_notification_service.py`

The agent must not update files outside this list.

## Execution Notes

### Plan

- Confirmed live Notification JSON/BSON schema from configurator (`Notification.yaml` 0.1.0.0): `_id`, `profile_id`, `customer_id`, `mentor_id` are objectId; no `saved` field; `dismissed` is a breadcrumb set by Discovery control (not shared).
- Removed `dismiss_notification` from shared `NotificationService`; kept `create_notification` and `get_notifications` (optional caller `match` kwarg, empty default).
- Updated `_check_permission` docstring to create/read only.
- Removed four dismiss unit tests; added `test_shared_service_has_no_dismiss_notification`.

### Configurator schema fetch

```bash
curl -X GET "http://localhost:8383/api/configurations/json_schema/Notification.yaml/latest/"
curl -X GET "http://localhost:8383/api/configurations/bson_schema/Notification.yaml/0.1.0.0/"
```

Both returned HTTP 200.

### Test results

- `PYTHONPATH=. pipenv run pytest tests/services/test_notification_service.py` — 8 passed
- `pipenv run test` — 267 passed
- `pipenv run lint` — R077 files black-clean; exit 1 from 24 pre-existing unrelated files
- `pipenv run build` — success (`api_utils-0.7.1`)
