# R071 – Scaffold NotificationService

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R069_add_ingress_collection_constants`  
**Description**: Add shared `NotificationService` for cross-domain notification documents (producers: Customer API, Admin SPA; dismiss: Discovery API). No harvest source exists yet — implement in api_utils.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md` — **MongoDB dictionary schemas**, **Standardized Get List pattern**
- `tasks/PENDING.R069.add_ingress_collection_constants.md`
- `tasks/SHIPPED.R049.add_list_query_utilities.md` — list pagination helpers
- `api_utils/config/config.py` — `NOTIFICATION_COLLECTION_NAME`
- `api_utils/services/event_service.py` — create + list reference
- `api_utils/mongo_utils/mongo_io.py`
- `api_utils/mongo_utils/list_query.py`
- `../mentorhub/Workshops/discovery_journey_issues.md` — Discovery owns dismiss mutation
- `../mentorhub/Workshops/customer_journey_issues_adjustments.md` — write vs read/dismiss split

### External prerequisite

F-D29 must deploy the **Notification** dictionary. If the configurator is unavailable, set **Status** to `Blocked` and stop.

RBAC list filtering (F-UA12) is **out of scope** — use a simple auth placeholder and optional `match` kwargs callers can extend later.

### MVP surface (api_utils)

- `create_notification(data, token, breadcrumb)` — encode ids; set `created` / `saved` breadcrumbs
- `get_notifications(token, breadcrumb, *, offset=0, size=20, match=None)` — offset/size list via `list_query.execute_list_query`; default sort newest first on `created.at_time`
- `dismiss_notification(notification_id, token, breadcrumb)` — update dismiss state + `saved` breadcrumb (field names from live schema)

## Goals

- `api_utils/services/notification_service.py` implements the three methods above.
- Uses `config.NOTIFICATION_COLLECTION_NAME`.
- Unit tests in `tests/services/test_notification_service.py`.
- `api_utils/services/__init__.py` exports `NotificationService`.

## Testing Expectations

- `pipenv run test tests/services/test_notification_service.py`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/notification_service.py`
- `api_utils/services/__init__.py` — export `NotificationService`
- `tests/services/test_notification_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
