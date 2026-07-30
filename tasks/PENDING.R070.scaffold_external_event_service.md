# R070 – Scaffold ExternalEventService

**Status**: Pending  
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
- `api_utils/config/config.py` — `EXTERNAL_EVENT_COLLECTION_NAME`
- `api_utils/services/event_service.py` — append/create pattern reference
- `api_utils/mongo_utils/mongo_io.py`
- `api_utils/mongo_utils/encode_properties.py`
- `../mentorhub/Workshops/admin_journey_issues.md` — F-AA02 goals
- `../mentorhub/Workshops/customer_journey_issues.md` — ExternalEvent dictionary summary

### External prerequisite

F-D29 must deploy the **ExternalEvent** dictionary to the configurator before integration tests can run. If `curl` for `ExternalEvent.yaml/latest` fails with the DB up (`pipenv run db`), set task **Status** to `Blocked` and stop — do not guess field shapes from workshop prose.

### MVP surface (api_utils)

- `create_external_event(data, token, breadcrumb)` — strip client `_id` / `created`; encode id fields per live schema; set `created` breadcrumb; `MongoIO.create_document` on `config.EXTERNAL_EVENT_COLLECTION_NAME`; **no update/delete**
- `_check_permission(token, operation)` — auth placeholder consistent with other services

Ingress-specific idempotency (external id dedup) may be added in Admin API (F-AA02) — keep api_utils layer thin.

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
- Optional when F-D29 is live: `pipenv run db` + `pipenv run integration` for one create round-trip (document in **Execution Notes** if skipped)

## Outputs

- `api_utils/services/external_event_service.py`
- `api_utils/services/__init__.py` — export `ExternalEventService`
- `tests/services/test_external_event_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
