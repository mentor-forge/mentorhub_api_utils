# R081 – Shared outbound RBAC match helper (F-UA12)

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R075_classmethod_and_data_boundary_contract`  
**Description**: Add a single outbound-RBAC helper used by every shared GET/list: build a Mongo match from the token (admin is unrestricted), AND search filters onto it without clobbering keys, and test a fetched document against the same match (get-by-id).

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md` — RBAC at the service layer
- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — consume vs control vs create
- `../mentorhub/Specifications/architecture.yaml`
- `README.md`
- `tasks/_PLANNING.md` — **Standardized Get List pattern** (search filters AND onto a base match)
- `tasks/_ORCHESTRATE.md`
- `api_utils/flask_utils/token.py` — token dict has `roles`, `profile_id`, `customer_id`, `mentor_id`
- `api_utils/config/config.py` — `ROLE_ADMIN`, `ROLE_MENTOR`, `ROLE_MENTEE`, `ROLE_CUSTOMER`
- `api_utils/mongo_utils/list_query.py` — `build_match_filter` currently **overwrites** same-key clauses
- `api_utils/services/resource_service.py` — prototype: non-admin `status != archived` on list only
- GitHub [F-UA12](https://github.com/mentor-forge/mentorhub_api_utils/issues/25) (this task); [F-UA13](https://github.com/mentor-forge/mentorhub_api_utils/issues/26) is the service-boundary split (R075–R079), not this helper

### Audit (today)

| Service | Inbound (`_check_permission` on write) | Outbound (what GET returns) |
|---------|----------------------------------------|-----------------------------|
| `ResourceService` | `pass` | list: non-admin `status != archived`; get-by-id **unfiltered** |
| `PathService`, `PlanService`, `NoteService`, `EventService`, `NotificationService`, `ExternalEventService` | `pass` or placeholder | none (or optional caller `match` / `profile_id` kwarg) |
| `ProfileService` | mentor/admin **403** on read | dashboard-shaped list (R076 strips this) |
| `JourneyService` | read `pass`; update/mutate/complete owner/mentee (R078 strips writes) | `get_journey` unfiltered |
| `EncounterService` | mentor/admin 403; owner on update | none |
| `MenteeService` | mentor/admin 403 on read and update | none |
| `AggregationService` | mentee required for `add_completion` | none |

Inbound write checks belong on **domain API subclasses** (R082 removes remaining write `_check_permission` from shared GETs; ISSUE artifacts specify API inbound). This task only adds the **outbound** primitives.

### Design

Admin (`ROLE_ADMIN` in `token["roles"]`) is **root**: outbound match is `{}` (sees archived and cross-tenant docs).

Non-admin: AND together the clauses the **caller** supplies (typically `status != archived` plus an `$or` of own `profile_id` / `customer_id` / `mentor_id`). If a required identity claim is missing, that clause is omitted; if **no** identity clauses remain and the spec requires a scope, use a match that yields zero documents (do **not** fall open).

Get-by-id: `MongoIO.get_document` then `matches_outbound(document, match)`. Miss → `HTTPNotFound` (not 403 — do not leak that a hidden id exists).

Search filters from `parse_list_request` / `build_match_filter` **AND** with outbound. Today `build_match_filter` assigns `match[field] = …` and would replace `status: {$ne: archived}` with a search `status` in_list. Fix that: when a key already exists, wrap colliding predicates in `$and` (or always `$and` outbound + search). Do not let a query param bypass outbound.

Encode ObjectId fields in outbound clauses with `encode_document` at the MongoIO boundary (same id fields as the collection).

Suggested module: `api_utils/services/rbac.py` (or `api_utils/mongo_utils/outbound.py` if you prefer it next to `list_query`). Export from `api_utils.services` and/or `api_utils.mongo_utils` so every service can call it.

Public functions (names may vary; keep them small and documented):

- `is_admin(token) -> bool`
- `build_outbound_match(token, clauses) -> dict` — `clauses` is a list of match dicts; admin returns `{}`
- `and_match(*parts) -> dict` — combine outbound + search without clobbering
- `matches_outbound(document, match) -> bool` — in-memory evaluate of the same predicates used for lists (enough for `$eq`, `$ne`, `$in`, `$or`, `$and`, field existence for `global`)
- `require_outbound(document, match)` — 404 if document is None or does not match

Do **not** apply the helper to services in this task — that is R082.

## Goals

- One reusable outbound helper; unit tests cover admin root, archived clause, `$or` identity clauses, empty-scope-not-open, `$and` with search `status`, get-by-id 404 on mismatch.
- `build_match_filter` (or the new `and_match`) no longer drops outbound `status` when search also filters `status`.
- No service behavior change except whatever `build_match_filter` fix requires for existing Resource tests (update those tests if the match shape becomes `$and`).

## Testing Expectations

- `pipenv run test tests/services/test_rbac.py` (or `tests/mongo_utils/test_outbound.py`)
- `pipenv run test tests/mongo_utils/test_list_query.py tests/services/test_resource_service.py`
- `pipenv run test`
- `pipenv run lint` — R081 files `black`-clean
- `pipenv run build`

## Outputs

- `api_utils/services/rbac.py` **or** `api_utils/mongo_utils/outbound.py` (new)
- `api_utils/services/__init__.py` and/or `api_utils/mongo_utils/__init__.py` — export the helper
- `api_utils/mongo_utils/list_query.py` — safe AND of base + search
- `tests/services/test_rbac.py` **or** `tests/mongo_utils/test_outbound.py`
- `tests/mongo_utils/test_list_query.py` — colliding `status` keys
- `tests/services/test_resource_service.py` — only if match shape changes

The agent must not update files outside this list.

## Execution Notes

Implemented `api_utils/services/rbac.py` with outbound RBAC helpers and moved `and_match` into `api_utils/mongo_utils/list_query.py` (re-exported from `mongo_utils` and `services`) to avoid circular imports between list_query and services.

**Public API (R082):**

| Module | Symbol | Purpose |
|--------|--------|---------|
| `api_utils.services.rbac` | `EMPTY_SCOPE_MATCH` | Zero-yield match when identity scope is required but empty |
| `api_utils.services.rbac` | `is_admin(token)` | True when `ROLE_ADMIN` in token roles |
| `api_utils.services.rbac` | `build_outbound_match(token, clauses)` | Admin → `{}`; else AND supplied clause dicts |
| `api_utils.mongo_utils.list_query` | `and_match(*parts)` | Merge match dicts without clobbering same-key clauses |
| `api_utils.services.rbac` | `matches_outbound(document, match)` | In-memory match evaluation for get-by-id |
| `api_utils.services.rbac` | `require_outbound(document, match, ...)` | Returns doc or raises `HTTPNotFound` |

`build_match_filter` now uses `and_match` so outbound `status != archived` survives search `status` filters.

**Tests:** 216 passed (`pipenv run test`), R081 files black-clean, build OK.
