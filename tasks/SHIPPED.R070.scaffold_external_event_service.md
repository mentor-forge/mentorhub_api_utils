# R070 – Scaffold ExternalEventService

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R069_add_ingress_collection_constants`  
**Description**: Add shared `ExternalEventService` for append-only ingress writes (Admin F-AA02). No harvest source exists yet — implement in api_utils following existing service conventions.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md` — **MongoDB dictionary schemas** (fetch live JSON schema from configurator)
- `tasks/PENDING.R069.add_ingress_collection_constants.md`
- `api_utils/config/config.py` — `EXTERNAL_EVENT_COLLECTION_NAME` (`ExternalEvent`)
- `api_utils/services/event_service.py` — append/create pattern reference
- `api_utils/mongo_utils/mongo_io.py`
- `api_utils/mongo_utils/encode_properties.py`
- `../mentorhub/Workshops/admin_journey_issues.md` — F-AA02 goals
- `../mentorhub_mongodb_api/configurator/configurations/ExternalEvent.yaml` — collection name and indexes (unique `source` + `external_id`)
- `../mentorhub_mongodb_api/configurator/dictionaries/ExternalEvent.0.1.0.yaml` — field names for planning; **do not** treat YAML as write source of truth

### External prerequisite

F-D29 **ExternalEvent** is in `mentorhub_mongodb_api` at version `0.1.0.0`. Execution must still fetch JSON/BSON schema from the **running configurator** per `_PLANNING.md`. If `curl` for `ExternalEvent.yaml/latest` fails with the DB up (`pipenv run db`), set task **Status** to `Blocked` and stop — do not guess field shapes from workshop prose or checked-in YAML.

Planning snapshot of dictionary fields (confirm live): `_id`, `source` (`external_event_source`: `stripe` \| `cognito`), `external_id`, `payload_hash`, `normalized_body`, `created`. Append-only — **no** `saved` breadcrumb.

### MVP surface (api_utils)

- `create_external_event(data, token, breadcrumb)` — strip client `_id` / `created`; encode id fields per live schema; set `created` breadcrumb; `MongoIO.create_document` on `config.EXTERNAL_EVENT_COLLECTION_NAME`; **no update/delete**
- `_check_permission(token, operation)` — auth placeholder consistent with other services

Ingress-specific idempotency (unique `source` + `external_id`) may be added in Admin API (F-AA02) — keep api_utils layer thin. Duplicate inserts may raise from the Mongo unique index; do not add a second lookup path here.

## Goals

- `api_utils/services/external_event_service.py` implements `ExternalEventService` with append-only create.
- Uses `config.EXTERNAL_EVENT_COLLECTION_NAME` (not a hard-coded string).
- Unit tests in `tests/services/test_external_event_service.py` with `@patch` on `MongoIO` / `Config`.
- `api_utils/services/__init__.py` exports `ExternalEventService`.

## Testing Expectations

- `pipenv run test tests/services/test_external_event_service.py`
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`
- Optional when configurator is live: `pipenv run db` + `pipenv run integration` for one create round-trip (document in **Execution Notes** if skipped)

## Outputs

- `api_utils/services/external_event_service.py`
- `api_utils/services/__init__.py` — export `ExternalEventService`
- `tests/services/test_external_event_service.py`

The agent must not update files outside this list.

## Execution Notes

### Plan
Append-only `ExternalEventService.create_external_event` following `EventService` conventions: strip client `_id`/`created`, `encode_document` at the MongoIO boundary, set `created` breadcrumb only (no `saved`), write via `MongoIO.create_document` on `config.EXTERNAL_EVENT_COLLECTION_NAME`. `_check_permission` is `pass` for any authenticated user. No update/delete, no duplicate-lookup idempotency. Export from `api_utils/services/__init__.py`.

### Live schema (configurator, 2026-08-22)
Fetched while DB/configurator was up (HTTP 200):

- JSON: `GET http://localhost:8383/api/configurations/json_schema/ExternalEvent.yaml/latest/`
- BSON: `GET http://localhost:8383/api/configurations/bson_schema/ExternalEvent.yaml/0.1.0.0/`

Fields: `_id`, `source` (enum `cognito`|`stripe`), `external_id`, `payload_hash`, `normalized_body` (object, additionalProperties true), `created` breadcrumb (`at_time`, `by_user`, `from_ip`, `correlation_id`). No `saved`.

**Id / date encoding (BSON authority):**
- `_id` → `objectId` → `ID_PROPERTIES = ["_id"]`
- `external_id` → **string** (provider message id) — do **not** encode as ObjectId
- `source`, `payload_hash` → string
- `created.at_time` → `date`; breadcrumbs already supply `datetime` (`create_flask_breadcrumb`), so `DATE_PROPERTIES = []` (same as EventService)

### Commands
- `PYTHONPATH=. pipenv run pytest tests/services/test_external_event_service.py -m "not e2e and not integration"` — 6 passed
- `pipenv run test` — 275 passed, 24 deselected
- `pipenv run lint` — fails on 25 **pre-existing** files (Black 3.12 vs 3.14 safety check). Scoped: `pipenv run black --check --target-version py312` on R070 files — pass
- `pipenv run build` — `api_utils-0.6.0` sdist + wheel succeeded
- Optional `pipenv run integration` create round-trip — **skipped** (no new integration test in Outputs; existing integration suite is Journey-only)

### Result
Status left **Pending** by execution agent; orchestrator confirmation: targeted 6 passed, `pipenv run test` 275 passed, build success. Status set to Shipped.
