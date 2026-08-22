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
- `api_utils/config/config.py` — `NOTIFICATION_COLLECTION_NAME` (`Notification`)
- `api_utils/services/event_service.py` — create + list reference
- `api_utils/mongo_utils/mongo_io.py`
- `api_utils/mongo_utils/list_query.py`
- `../mentorhub/Workshops/discovery_journey_issues.md` — Discovery owns dismiss mutation
- `../mentorhub/Workshops/customer_journey_issues_adjustments.md` — write vs read/dismiss split
- `../mentorhub_mongodb_api/configurator/configurations/Notification.yaml` — collection name and indexes
- `../mentorhub_mongodb_api/configurator/dictionaries/Notification.0.1.0.yaml` — field names for planning; **do not** treat YAML as write source of truth

### External prerequisite

F-D29 **Notification** is in `mentorhub_mongodb_api` at version `0.1.0.0`. Execution must still fetch JSON/BSON schema from the **running configurator**. If the configurator is unavailable, set **Status** to `Blocked` and stop.

RBAC list filtering (F-UA12) is **out of scope** — use a simple auth placeholder and optional `match` kwargs callers can extend later.

### Schema notes (confirm live)

Planning snapshot of dictionary fields (confirm via configurator before coding):

| Field | Role |
| --- | --- |
| `_id` | identifier |
| `name` | searchable / display title (`word`) |
| `message` | user-facing body (`sentence`) — **not** `description` |
| `profile_id` / `customer_id` / `mentor_id` | optional target identifiers (sibling fields; omit unused) |
| `global` | optional published-at breadcrumb when targeting is global |
| `link_metadata` | optional object |
| `dismissed` | breadcrumb set on dismiss — **not** a boolean |
| `cancelled` | breadcrumb set when cancelled / superseded |
| `created` | breadcrumb |
| `status` | `default_status` (`active` / `archived`); distinct from dismissed/cancelled |

There is **no** `saved` breadcrumb on Notification. Do not write `saved` on create or dismiss.

Do **not** assume a nested `scope_id` wrapper unless the live JSON schema uses one — current dictionary models targeting as optional sibling fields.

### MVP surface (api_utils)

- `create_notification(data, token, breadcrumb)` — encode ids; set `created` breadcrumb (not `saved`)
- `get_notifications(token, breadcrumb, *, offset=0, size=20, match=None)` — offset/size list via `list_query.execute_list_query`; default sort newest first on `created.at_time`
- `dismiss_notification(notification_id, token, breadcrumb)` — set `dismissed` breadcrumb from live schema (do not invent a boolean or `saved` field)

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
