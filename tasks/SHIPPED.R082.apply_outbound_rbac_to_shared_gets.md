# R082 – Apply F-UA12 outbound filters to every shared GET

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R076_shared_profile_get_and_create`, `R077_shared_notification_get_and_create`, `R078_strip_journey_control_mutations`, `R079_strip_remaining_control_mutations`, `R081_outbound_rbac_helper`  
**Description**: Wire the R081 helper into every shared list and get-by-id. Outbound (what a caller can see) lives only in api_utils. Inbound (who may create/update) is not implemented here — ISSUE artifacts tell domain APIs to add write `_check_permission`. Admin is unrestricted. Remove leftover inbound-on-read 403s from shared services.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml` — `controls` / `creates` / `consumes`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/PENDING.R081.outbound_rbac_helper.md` — helper API (treat as SHIPPED if already renamed)
- `api_utils/flask_utils/token.py` — `profile_id`, `customer_id`, `mentor_id`, `roles`
- Every `api_utils/services/*_service.py` GET/list method
- Matching `tests/services/test_*_service.py`

Confirm `status` / id field names from the **running configurator** BSON/JSON schema. If unavailable, set **Status** to `Blocked`.

### Split of responsibility (F-UA12 + F-UA13)

- **Outbound (this repo, this task):** GET/list visibility. Build match from role + token ids; AND list search filters; get-by-id post-fetch `require_outbound`.
- **Inbound (domain API subclass):** who may POST/PATCH/mutate. Shared `create_event` / `create_notification` / `create_profile` stay callable without a write role check; the API subclass adds `_check_permission` for control writes. Delete shared write `_check_permission` branches still present after R078/R079 (Encounter/Mentee/Profile read 403s, etc.). Shared read `_check_permission` may `pass` (token already required by the route).

### Per-collection outbound (non-admin)

Admin (`ROLE_ADMIN`): match `{}` on every collection.

Encode ids. Omit a token-id clause when that claim is empty. If a scoped collection would have **zero** identity clauses, do not fall open.

| Shared service | List / get-by-id clauses (AND) |
|----------------|--------------------------------|
| `ResourceService`, `PathService`, `PlanService` | `status != archived`. Catalog consume: mentee/discovery/mentor all see non-archived. `get_resources_by_ids` filters the result list the same way. |
| `ProfileService` | `status != archived` (Profile uses `profile_status`, still has `archived`). `$or`: `_id`/`name` is caller (`token.profile_id` or `token.user_id`); `customer_id == token.customer_id` if set; `mentor_id == token.mentor_id` or caller profile id if set. `get_profile_by_token` stays identity lookup (caller’s own row) and does **not** need the list `$or`. |
| `JourneyService` | `status != archived`. `$or`: `profile_id`/`_id == token.profile_id`; journeys whose profile is in-scope via the same customer/mentor rules **only if** those fields exist on Journey (they do not today — then own-profile only). `get_journey_progress` is a consume aggregation: apply the same visibility to the underlying journey (404/zeros if outbound fails). |
| `NoteService` | `status != archived`. `$or`: `profile_id == token.profile_id`; `customer_id` if the Note schema has it (it may not — then own-profile only). Existing `resource_id` scope stays AND with outbound. |
| `EventService` | `$or` on `context.profile_id` / `profile_id` == `token.profile_id` (and customer/mentor if those fields exist on Event). Optional `profile_id=` kwarg must **narrow** outbound, never widen it. |
| `NotificationService` | `status != archived`. `$or`: `profile_id`, `customer_id`, `mentor_id` vs token; or `global` exists. Optional extra `match` kwargs AND with outbound, never replace it. |
| `EncounterService` | `status != archived` if present. `$or`: `mentor_id` equals `token.mentor_id` or caller profile id; `mentee_id` equals `token.profile_id`. Remove mentor-role **403** on read. |
| `MenteeService` | `status != archived` if present. Scope to mentee notes the caller may see (mentor of that profile, or own profile, or admin). Remove mentor-role **403** on read. 404 if missing (R079) **or** outbound miss. |
| `AggregationService` | same visibility as Resource (if the aggregation exists but the Resource would be hidden, 404/None). |
| `ExternalEventService` | if a GET is added in R079, non-admin match should yield nothing (Admin **controls**; not a consume collection) unless admin. Create stays shared append-only. |

### Get-by-id

Every `get_<doc>(id, token, …)`: load via MongoIO, then `require_outbound`. Missing **or** filtered out → `HTTPNotFound`. Resource `get_resource` composite: hide the whole payload if the Resource fails outbound.

### Tests

Replace “placeholder `_check_permission` allows all” and mentor-admin 403-on-read tests with outbound cases:

- admin sees archived
- mentee/customer does not see archived on list or get-by-id
- get-by-id of someone else’s Profile/Journey → 404
- list search `status=archived` does not return archived for non-admin
- Notification `$or` includes `global` and own ids

## Goals

- Every shared GET/list uses R081 outbound + AND’d search filters.
- Get-by-id applies the same filter post-fetch.
- Shared services do not 403 on read for “wrong role”; they filter.
- No inbound write RBAC added on shared classes.

## Testing Expectations

- `pipenv run test tests/services/`
- `pipenv run test`
- `pipenv run lint` — R082 files `black`-clean
- `pipenv run build`

## Outputs

- `api_utils/services/resource_service.py`
- `api_utils/services/path_service.py`
- `api_utils/services/plan_service.py`
- `api_utils/services/profile_service.py`
- `api_utils/services/journey_service.py`
- `api_utils/services/note_service.py`
- `api_utils/services/event_service.py`
- `api_utils/services/notification_service.py`
- `api_utils/services/encounter_service.py`
- `api_utils/services/mentee_service.py`
- `api_utils/services/aggregation_service.py`
- `api_utils/services/external_event_service.py` — only if GET exists
- `tests/services/test_*.py` for each service touched

The agent must not update files outside this list. (README / version bump is R080 — major `1.0.0`.)

## Execution Notes

Confirmed field names from running configurator BSON schemas (all collections at `0.1.0.0`). Wired R081 helpers into every shared GET/list:

- Catalog services (Resource, Path, Plan): `status != archived`; admin unrestricted.
- Profile: archived filter + identity `$or` on `_id`, `name`, `customer_id`, `mentor_id`; `get_profile_by_token` unchanged.
- Journey: own-profile `$or`; removed mentor-role 403 from `get_journey_progress` (returns zeros when outbound fails).
- Note: own-profile `$or` AND existing `resource_id` scope.
- Event: `$or` on `context.profile_id` / `profile_id`; optional `profile_id` kwarg narrows via `and_match`.
- Notification: archived filter + `$or` including `global`; extra `match` AND'd with outbound.
- Encounter / Mentee: removed read 403s; outbound `$or` / mentor-of-profile check; 404 on miss.
- Aggregation: returns `None` when parent Resource fails outbound.
- ExternalEvent GET: non-admin `EMPTY_SCOPE_MATCH`; admin unrestricted.

**Tests:** 123 service tests + 225 unit tests passed; R082 files black-clean; build OK.
