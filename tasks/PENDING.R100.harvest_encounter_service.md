# R100 – Harvest `EncounterService` into `api_utils.services`

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Move the Encounter domain from
`mentorhub_mentor_api/src/services/encounter_service.py` into a new shared
`api_utils.services.EncounterService`, preserving behavior exactly — including
agenda auto-fill from the referenced Plan, owner-or-admin patch semantics, and
the optional scoped per-mentee reads used by the Profile composites.

## Context / Input files

- `mentorhub_mentor_api/src/services/encounter_service.py` (source of truth)
- `mentorhub_api_utils/api_utils/services/plan_service.py` (from R090)
- `mentorhub_api_utils/api_utils/services/profile_service.py` (from R120)
- `mentorhub_api_utils/api_utils/mongo_utils/encode_properties.py` (`encode_document`)
- `mentorhub_api_utils/api_utils/config/config.py` (`ENCOUNTER_COLLECTION_NAME`, `ROLE_MENTOR`, `ROLE_ADMIN`)
- `mentorhub_mentor_api/tasks/SHIPPED.L090.encounter_create_required_fields_and_agenda_autofill.md`
- `mentorhub_mentor_api/tasks/SHIPPED.L100.encounter_rbac_read_and_owner_patch.md`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Create `api_utils/services/encounter_service.py` with `EncounterService`:
  - `create_encounter(data, token, breadcrumb)` — require
    `mentor_id`/`mentee_id`/`plan_id` (delegated to the collection
    `$jsonSchema` validator as in the source); fetch the referenced Plan via
    `PlanService.get_plan` (missing Plan → `HTTPNotFound`); auto-fill `agenda`
    from the Plan checklist via `_build_agenda_from_plan` (overriding any
    client-supplied agenda); drop client `_id`; `encode_document(data,
    ["mentor_id", "mentee_id", "plan_id"], [])`; stamp `created`/`saved`; return id.
  - `get_encounter(encounter_id, token, breadcrumb)` — mentor/admin read;
    `HTTPNotFound` when missing.
  - `update_encounter(encounter_id, data, token, breadcrumb)` — gate on role
    first, load the doc (404 before ownership check), then **owner-or-admin**
    check (admins any; other mentors must have caller Profile `_id` ==
    `encounter.mentor_id`, resolved via `ProfileService.get_profile_by_token`);
    restricted-field guard; `$set` + `saved`.
  - `get_encounters_for_mentee(mentee_id, token, breadcrumb, offset=None,
    size=None)` — mentor/admin read; match on `_normalize_mentee_id(mentee_id)`;
    `date`-desc; **optional** `skip`/`limit` only when both `offset` and `size`
    are provided (full list otherwise, for composite callers).
  - `get_recent_encounter(mentee_id, token, breadcrumb)` — latest-by-`date`
    summary (`_id`, `date`, `tldr`, `summary`) or `None`.
  - Preserve helpers `_check_permission` (mentor/admin read; owner-or-admin when
    `encounter` supplied), `_validate_update_data`, `_build_agenda_from_plan`,
    `_normalize_mentee_id` exactly.
- Use **lazy imports** for `PlanService` and `ProfileService` inside methods to
  avoid the Encounter↔Profile import cycle (mirroring the mentor source).
- MongoIO-only access; no direct PyMongo.

## Files to modify / create

- **Create**: `api_utils/services/encounter_service.py`
- **Modify**: `api_utils/services/__init__.py` (export `EncounterService`)
- **Create**: `tests/services/test_encounter_service.py`
  (create+agenda-from-plan, missing-plan 404, read RBAC, owner-or-admin patch,
  restricted-field guard, scoped/unscoped per-mentee reads, recent summary)

## Testing expectations

- `pipenv run db`, then `pipenv run test` green.
- `pipenv run lint` and `pipenv run build` clean.

## Packaging / build checks

- All suites pass; version bump deferred to **R140**.

## Dependencies / Ordering

- **Depends On**: R040, R090 (Plan). Composes with **R120** (Profile) via lazy
  import — Profile detail lists encounters and the owner-patch resolves the
  caller Profile — so R120 must also be present before either task's tests are
  finalized. Recommended sequence: R090 → R110 → R120 → **R100**.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Created shared `EncounterService` with all methods + helpers.
- [ ] Preserved agenda-from-Plan, owner-or-admin patch, scoped reads.
- [ ] Used lazy imports for Plan/Profile (no import cycle).
- [ ] Exported from `api_utils.services`.
- [ ] Added tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
