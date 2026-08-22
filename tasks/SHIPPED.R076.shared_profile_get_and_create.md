# R076 – Shared Profile GET (RBAC) and global create

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R075_classmethod_and_data_boundary_contract`  
**Description**: Make `ProfileService` a consume + immutable-create service: plain GET / list with RBAC filter, plus `create_profile` for Admin and Customer. Move Mentor-dashboard enrich out of the shared class.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml` — Customer **controls** Profile; Admin **creates** Profile; Discovery and Mentor **consume** Profile
- `README.md`
- `tasks/_PLANNING.md` — **MongoDB dictionary schemas**
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R065.harvest_encounter_and_profile_services.md` — current mentor-shaped methods
- `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md` — dashboard enrich returns here
- `api_utils/services/profile_service.py`
- `tests/services/test_profile_service.py`
- `api_utils/mongo_utils/list_query.py` — offset/size list helpers
- `api_utils/services/path_service.py` — list + get-by-id reference
- `api_utils/services/event_service.py` — global POST reference

Fetch live Profile JSON/BSON schema from the running configurator before coding. If unavailable, set **Status** to `Blocked` and stop.

### Keep on shared `ProfileService`

| Method | Behavior |
|--------|----------|
| `get_profile_by_token` | Resolve caller Profile (`name == token.user_id`); return `None` if missing |
| `get_profile` | Single document by id; **404** if missing; **no** mentee/encounter composite |
| `get_profiles` | Offset/size list via `execute_list_query`; RBAC `base_match` (see below); **not** the Mentor Dashboard |
| `create_profile` | Global POST: strip client `_id`/`created`/`saved`; stamp breadcrumbs; `encode_document` at MongoIO boundary |

### Move to Mentor API subclass (do not keep in api_utils)

Current `get_profiles` (dashboard cards + journey progress + last encounter), current `get_profile` composite `{profile, mentee, encounters}`, and `get_profile_properties` plus private `_resource_ref` / `_load_resource` / `_mentor_history`. Capture signatures and behavior in `ISSUE.mentorhub_mentor_api.extend_shared_services.md` if that file still has placeholders; do not invent new dashboard logic here.

### RBAC

Do **not** invent a one-off list `base_match` in this task. F-UA12 outbound filters (role/token `status != archived`, customer/mentor/own-profile scope, get-by-id post-fetch) land in **R082**. Here, `get_profiles` / `get_profile` require a valid token only (`_check_permission` for read/create may `pass`). Search query filters still AND via `build_match_filter` with an empty `base_match`.

`_check_permission` for **create** stays a no-op on the shared class — Admin and Customer subclasses add inbound write checks (see `ISSUE.mentorhub_customer_api.profile_control.md` / `ISSUE.mentorhub_admin_api.profile_create.md`). Do **not** require mentor/admin for shared reads.

## Goals

- Shared Profile surface is GET-by-id, GET-by-token, paginated list (empty outbound match until R082), and `create_profile`.
- Mentor-only enrich methods are gone from `api_utils`.
- Unit tests cover create, get-by-id 404, and `get_profile_by_token`. Outbound RBAC assertions wait for R082.
- MongoDB I/O via **MongoIO** only.

## Testing Expectations

- `pipenv run test tests/services/test_profile_service.py`
- `pipenv run test`
- `pipenv run lint` — R076 files `black`-clean
- `pipenv run build`

## Outputs

- `api_utils/services/profile_service.py`
- `tests/services/test_profile_service.py`
- `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md` — only if needed to record removed enrich method bodies

The agent must not update files outside this list.

## Execution Notes

### Live schema fetch (prerequisite)

Configurator reachable at `http://localhost:8383`. Both schemas fetched before coding:

```bash
curl -X GET "http://localhost:8383/api/configurations/json_schema/Profile.yaml/latest/" -H "accept: application/json"
curl -X GET "http://localhost:8383/api/configurations/bson_schema/Profile.yaml/0.1.0.0/" -H "accept: application/json"
```

BSON storage types that drive `encode_document` at the MongoIO boundary:

| Field | bsonType |
|-------|----------|
| `_id`, `customer_id`, `mentor_id` | `objectId` |
| `experience[].roles[].start` / `.end` | `date` |
| `created.at_time`, `saved.at_time` | `date` (breadcrumb already supplies `datetime`) |
| `name`, `full_name`, `email`, `description`, `cognito_sub` | `string` |
| `status` | `string` enum `active`/`archived`/`provisioned`/`suspended` |
| `roles` | array of `string` enum `admin`/`coordinator`/`customer`/`mentee`/`mentor` |
| `interests` | array of `string` enum |
| `email_verified` | `bool` |

So `ID_PROPERTIES = ["_id", "customer_id", "mentor_id"]` and
`DATE_PROPERTIES = ["start", "end"]` (the nested experience role dates;
`encode_document` recurses into nested dicts and dict lists).

### Plan

1. Rewrite `api_utils/services/profile_service.py` as a consume + immutable-create
   service with four public `@classmethod`s: `get_profile_by_token`,
   `get_profile`, `get_profiles`, `create_profile`.
2. `_check_permission` becomes a no-op (`pass`) for read and create. Shared reads
   no longer require mentor/admin; Admin and Customer subclasses add inbound
   write checks.
3. `get_profiles` uses the standardized offset/size list pattern:
   `build_match_filter({}, filters, PROFILE_LIST_FILTERS)` +
   `build_sort_by` + `execute_list_query`. `base_match` stays empty — outbound
   RBAC filters land in R082.
4. `get_profile` returns the plain document and raises `HTTPNotFound`; no
   mentee/encounter composite.
5. `create_profile` strips `_id`/`created`/`saved` from client data, calls
   `encode_document`, stamps both breadcrumbs, and inserts via
   `MongoIO.create_document`.
6. Export `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER` for subclasses (the
   Customer ISSUE asks for these).
7. Delete the Mentor-dashboard enrich (`get_profiles` cards, composite
   `get_profile`, `get_profile_properties`, `_resource_ref`, `_load_resource`,
   `_mentor_history`) and the lazy Journey/Mentee/Encounter imports that only
   existed to serve them.
8. Rewrite `tests/services/test_profile_service.py` for the new surface.

`tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md` needs **no** edit:
it has no placeholders and already records that the dashboard enrich methods
live in `mentorhub_mentor_api/src/services/profile_service.py` (verified —
`get_profiles`, `get_profile`, `_mentor_history`, `get_profile_properties` are
all still present there), with a table row telling that repo to rename or
override them against the shared class.

Unexpected errors keep propagating raw (unchanged from the current service) so
the route layer's `@handle_route_exceptions` produces the 500; only domain
exceptions are raised here.

### Summary of changes

`api_utils/services/profile_service.py` rewritten. Shared surface is now:

| Method | Behavior |
|--------|----------|
| `get_profile_by_token` | Unchanged — `match={"name": token.user_id}`, returns `None` if missing |
| `get_profiles` | Offset/size page via `execute_list_query`; empty `base_match`; `PROFILE_LIST_FILTERS` AND-ed in via `build_match_filter`; default sort `name asc` |
| `get_profile` | Plain `MongoIO.get_document`; `HTTPNotFound` if missing; no composite |
| `create_profile` | Strips `_id`/`created`/`saved`, `encode_document`, stamps `created` + `saved`, `MongoIO.create_document`, backfills `_id` |

`_check_permission` is now a no-op for read and create (was mentor-or-admin,
which 403'd shared GETs). New module constants `ID_PROPERTIES`,
`DATE_PROPERTIES`, `SYSTEM_MANAGED_FIELDS`, `PROFILE_LIST_FILTERS`,
`PROFILE_LIST_ORDER`. All methods remain `@classmethod` with `cls` dispatch
(R075 contract preserved).

Removed (now Mentor-API-only): dashboard-shaped `get_profiles`, composite
`get_profile`, `get_profile_properties`, `_resource_ref`, `_load_resource`,
`_mentor_history`, and the lazy `JourneyService` / `MenteeService` /
`EncounterService` imports that served them. `pymongo.ASCENDING` and
`HTTPForbidden` imports dropped with them.

`tests/services/test_profile_service.py` rewritten — 12 tests covering
get-by-token (hit and miss), list pagination/filters/any-role, get-by-id
(document, 404, raw error propagation), create (breadcrumbs + ObjectId
encoding, system-managed field stripping), no-op `_check_permission`, and a
guard that the enrich methods are gone from the shared class. No outbound RBAC
assertions — those belong to R082.

No edit to `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md`: it had
no placeholders and the removed method bodies still exist verbatim in
`mentorhub_mentor_api/src/services/profile_service.py`.

`EncounterService` still calls `ProfileService.get_profile_by_token` for its
owner check; that method is unchanged, and the Encounter tests confirm it.

### Test results

| Command | Result |
|---------|--------|
| `pipenv run test tests/services/test_profile_service.py` | Pass — the Pipfile `test` script hardcodes `tests/`, so the path arg is ignored and the full suite runs |
| `PYTHONPATH=. pipenv run pytest tests/services/test_profile_service.py -v -m "not e2e and not integration"` | Pass — 12 passed (scoped file actually exercised) |
| `pipenv run test` | Pass — 270 passed, 24 deselected |
| `pipenv run lint` | R076 files `black`-clean (`black --check` on both returns 0). 24 pre-existing files in the repo still fail `black --check`; none are R076 outputs and none were touched |
| `pipenv run build` | Pass — built `api_utils-0.7.1.tar.gz` and `api_utils-0.7.1-py3-none-any.whl` |

### Follow-ups

- R082 supplies the outbound RBAC `base_match` for `get_profiles` and the
  post-fetch check for `get_profile`; the empty-match seam is marked with a
  comment in the service.
- Repo-wide `black` debt (24 files) predates this task and is out of scope here.
