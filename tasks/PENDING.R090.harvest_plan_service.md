# R090 – Harvest `PlanService` into `api_utils.services`

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Move the Plan domain from `mentorhub_mentor_api/src/services/plan_service.py`
into a new shared `api_utils.services.PlanService`, preserving behavior exactly.
Encounter (R100) depends on this for its agenda-from-Plan auto-fill.

## Context / Input files

- `mentorhub_mentor_api/src/services/plan_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/mongo_utils/list_query.py` (from R040)
- `mentorhub_api_utils/api_utils/config/config.py` (`PLAN_COLLECTION_NAME`)
- `mentorhub_mentor_api/tasks/SHIPPED.L070.implement_plan_steps_service.md`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Create `api_utils/services/plan_service.py` with `PlanService`:
  - `create_plan(data, token, breadcrumb)` — drop client `_id`, stamp
    `created`/`saved`, `create_document` into `PLAN_COLLECTION_NAME`, return id.
  - `get_plans(token, breadcrumb, offset=DEFAULT_OFFSET, size=DEFAULT_SIZE,
    filters=None, sort_by=None)` — shared offset/size header pagination, optional
    `name` **contains** filter, default **name asc**, via `build_match_filter`/
    `build_sort_by`/`execute_list_query`; returns a plain list.
  - `get_plan(plan_id, token, breadcrumb)` — by-id read; `HTTPNotFound` missing.
  - `update_plan(plan_id, data, token, breadcrumb)` — restricted-field guard
    (`_id`/`created`/`saved`), `$set` + `saved` breadcrumb; `HTTPNotFound` missing.
  - Preserve the module-level `PLAN_LIST_FILTERS` / `PLAN_LIST_ORDER` specs.
- Preserve the `steps`⇄`checklist` semantics relied on by Encounter's agenda
  auto-fill (`_build_agenda_from_plan` reads `plan.get("steps") or
  plan.get("checklist")`); keep whatever `steps`/`checklist` shaping the mentor
  Plan service/route contract requires so R100 behaves identically.
- Preserve `_check_permission` placeholder (authenticated-only) exactly.
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Create**: `api_utils/services/plan_service.py`
- **Modify**: `api_utils/services/__init__.py` (export `PlanService`,
  `PLAN_LIST_FILTERS`, `PLAN_LIST_ORDER`)
- **Create**: `tests/services/test_plan_service.py`
  (create/list pagination+filter+order/get/update, restricted-field guard)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040. Blocker for **R100** (Encounter agenda-from-Plan).
  Independent of R050/R060/R070/R080/R110.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Created shared `PlanService` (create/list/get/update) + specs.
- [ ] Preserved `steps`⇄`checklist` semantics for Encounter agenda.
- [ ] Exported from `api_utils.services`.
- [ ] Added tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
