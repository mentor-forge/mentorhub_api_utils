# R071 – Scaffold NotificationService

**Status**: Shipped  
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

### Plan
1. Fetch live JSON + BSON schemas from the running configurator (`Notification.yaml` latest / `0.1.0.0`).
2. Implement `NotificationService` in Event/ExternalEvent style: MongoIO only, `config.NOTIFICATION_COLLECTION_NAME`, encode ids at the MongoIO boundary, `created` on create, `dismissed` breadcrumb on dismiss, no `saved`.
3. Export `NotificationService` from `api_utils/services/__init__.py` without dropping `ExternalEventService`.
4. Unit-test create / list / dismiss / strip client ids / no `saved` with `@patch` on MongoIO / Config.

### Live schema (source of truth)

Fetched 2026-08-22 from configurator:

- JSON: `GET http://localhost:8383/api/configurations/json_schema/Notification.yaml/latest/`
- BSON: `GET http://localhost:8383/api/configurations/bson_schema/Notification.yaml/0.1.0.0/`

**Fields (no nested `scope_id`; no `saved`):** `_id`, `name`, `message` (user-facing body, not `description`), optional sibling `profile_id` / `customer_id` / `mentor_id`, optional `global` breadcrumb, optional `link_metadata` object, `dismissed` breadcrumb, `cancelled` breadcrumb, `created` breadcrumb, `status` enum `active`/`archived` (`default_status`).

**Id / date encoding (BSON):**
- objectId: `_id`, `profile_id`, `customer_id`, `mentor_id`
- date: breadcrumb `at_time` (`created`, `dismissed`, `cancelled`, `global`)
- string: `name`, `message`, `status`, breadcrumb `by_user` / `correlation_id` / `from_ip`

**`dismissed` breadcrumb shape:** `{ from_ip, by_user, at_time, correlation_id }` — same as `created` / `cancelled` / `global`. Not a boolean.

**Encoding choices:** `ID_PROPERTIES = ["_id", "profile_id", "customer_id", "mentor_id"]`; `DATE_PROPERTIES = []` (breadcrumbs already supply datetime). Create sets only `created`. Dismiss `$set`s only `dismissed`. Never write `saved`.

### Implementation
- `api_utils/services/notification_service.py` — `create_notification`, `get_notifications` (offset/size via `list_query.execute_list_query`, default sort `created.at_time` desc, optional `match`), `dismiss_notification` (`MongoIO.update_document(..., set_data={"dismissed": breadcrumb})`). Auth placeholder `pass`. Strips `_id` / `created` / `dismissed` / `cancelled` / `saved` on create.
- `api_utils/services/__init__.py` — import + `__all__` for `NotificationService`; `ExternalEventService` retained.
- `tests/services/test_notification_service.py` — 11 mocked unit tests.

### Commands / results
- `PYTHONPATH=. pipenv run pytest tests/services/test_notification_service.py -m "not e2e and not integration"` — **11 passed**
- `pipenv run test` — **286 passed**, 24 deselected
- `pipenv run lint` — fails on pre-existing files; `black --check` on R071 files **passed** after formatting `notification_service.py` and the test
- `pipenv run build` — **api_utils-0.6.0** sdist + wheel succeeded

Status left **Pending** by execution agent; orchestrator confirmation: targeted 11 passed, `pipenv run test` 286 passed, build success. Status set to Shipped.
