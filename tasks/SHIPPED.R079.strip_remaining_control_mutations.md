# R079 – Strip remaining control POST/PATCH/mutate and BFF enrich from shared services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R075_classmethod_and_data_boundary_contract`  
**Description**: Apply the same data-boundary split to Note, Plan, Encounter, Mentee, Aggregation, Path, and Resource: shared GET / list with RBAC; control writes and enrich move to the controlling API subclass (documented in ISSUE files).

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md`
- `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md`
- Each `api_utils/services/{note,plan,encounter,mentee,aggregation,path,resource}_service.py` and matching `tests/services/test_*_service.py`

If a removed method body is not already in the target ISSUE, **append it** to that ISSUE (classmethod form) before deleting it from api_utils so no control logic is lost.

### Per-service split

| Shared service | Keep | Remove (controlling API) |
|----------------|------|--------------------------|
| `NoteService` | `get_notes_for_resource`, `list_all_notes_for_resource`; `_check_permission` read | `create_note` → Mentee (**controls** Note) |
| `PlanService` | `get_plans`, `get_plan`; list filter/order constants | `create_plan`, `update_plan`, `_validate_update_data` → Mentor |
| `EncounterService` | `get_encounter`, `get_encounters_for_mentee`, `get_recent_encounter`, `_normalize_mentee_id`; read RBAC | `create_encounter`, `update_encounter`, `_build_agenda_from_plan`, `_validate_update_data`; owner-or-admin write RBAC → Mentor |
| `MenteeService` | `get_mentee` **read-only** (404 if missing; no create-if-missing) | `update_mentee`, `_default_document`, `_validate_update_data`, create-if-missing branch → Mentor |
| `AggregationService` | `get_aggregation_for_resource` (no implicit create); duration helpers needed only if still used by GET | `add_hit`, `add_completion`, `_get_or_create_aggregation` write path, `get_aggregation_detail` (enrich + create-if-missing) → Mentee |
| `PathService` | `get_paths`, `get_path` returning the **raw** Path document | `_collect_resource_ids`, `_enrich_path_resources`, and enrich inside `get_path` → Mentee BFF (Mentor already has a raw local get) |
| `ResourceService` | existing GETs (already consume-only) | none. Keep archived `base_match` for non-admin as the RBAC list filter |
| `ExternalEventService` | keep `create_external_event` (append-only immutable create); add `get_external_event` by id if missing | no PATCH |

### RBAC on remaining GETs

- **Note / Path / Resource / Plan / Encounter / Aggregation:** authenticated read; keep any existing non-admin archived filter on Resource. Encounter/Mentee/Plan read may keep mentor-or-admin if that matches current tests — do not silently open mentor-only collections to all roles.
- Do not add new write `_check_permission` branches on shared classes.

### Tests

Delete unit tests for removed methods from this repo. Keep GET tests; update Path `get_path` tests so nested `resources` stay ids, not summaries. Update Mentee `get_mentee` tests for 404-if-missing.

## Goals

- Shared services for these collections are consume GETs (plus ExternalEvent create).
- Removed method bodies exist in the ISSUE artifacts for Mentee/Mentor.
- Full unit suite green.

## Testing Expectations

- `pipenv run test tests/services/`
- `pipenv run test`
- `pipenv run lint` — R079 files `black`-clean
- `pipenv run build`

## Outputs

- `api_utils/services/note_service.py`
- `api_utils/services/plan_service.py`
- `api_utils/services/encounter_service.py`
- `api_utils/services/mentee_service.py`
- `api_utils/services/aggregation_service.py`
- `api_utils/services/path_service.py`
- `api_utils/services/resource_service.py` — only if RBAC/docs comments change
- `api_utils/services/external_event_service.py` — only if adding GET
- `tests/services/test_note_service.py`
- `tests/services/test_plan_service.py`
- `tests/services/test_encounter_service.py`
- `tests/services/test_mentee_service.py`
- `tests/services/test_aggregation_service.py`
- `tests/services/test_path_service.py`
- `tests/services/test_resource_service.py` — only if comments/assertions change
- `tests/services/test_external_event_service.py` — only if GET is added
- `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md` — append any missing removed bodies
- `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md` — append any missing removed bodies

The agent must not update files outside this list.

## Execution Notes

**Approach:** Stripped write/mutate methods and BFF enrich from eight shared services per the split table. Harvest-back bodies appended to Mentee ISSUE (already had Note/Path/Aggregation) and Mentor ISSUE (Plan/Encounter/Mentee writes). `ExternalEventService.get_external_event` added. `MenteeService.get_mentee` now 404-if-missing. `PathService.get_path` returns raw document. Encounter read RBAC simplified (write ownership removed).

**Ripple (required for green suite):** Removed link→`AggregationService.add_hit` side effect from shared `EventService.create_event` and deleted three dependent unit tests; documented restore on Mentee `EventService` subclass in Mentee ISSUE.

**Tests:** `PYTHONPATH=. pipenv run pytest tests/services/` — 100 passed; `pipenv run test` — all passed; `pipenv run lint` — clean on R079 files; `pipenv run build` — success.
