# R059 – Harvest Journey promote mutations into JourneyService

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Merge `promote_path_to_next`, `promote_module_to_next`, and private helpers from `mentorhub_mentee_api` temporary `JourneyPromoteService` onto `api_utils.services.journey_service.JourneyService`. Port unit tests. Mutation methods return plain Journey documents (no `profile` enrichment).

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Source service: `../mentorhub_mentee_api/src/services/journey_promote_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_journey_promote_service.py`
- Target: `api_utils/services/journey_service.py`
- Target tests: `tests/services/test_journey_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/SHIPPED.R046.harvest_journey_service.md` — original JourneyService harvest pattern
- `../mentorhub_mentee_api/src/services/journey_promote_service.py`
- `../mentorhub_mentee_api/test/services/test_journey_promote_service.py`
- `../mentorhub_mentee_api/tasks/ISSUE.mentorhub_api_utils.harvest_journey_promote_mutations.md` — behavior summary
- `api_utils/services/journey_service.py` — existing class (`_check_permission`, `_validate_object_id`, `_normalize_id`, advance/complete)
- `api_utils/config/config.py` — `PATH_COLLECTION_NAME`, `JOURNEY_COLLECTION_NAME`

### Behavior to harvest

| Method | Behavior |
|--------|----------|
| **`promote_path_to_next(path_id, token, breadcrumb)`** | Copy **all** `Path.modules[]` onto Journey `next[]`; remove Path id from `journey.later[]`. Return updated Journey document. |
| **`promote_module_to_next(path_id, module_name, token, breadcrumb)`** | Copy **one** module (by `module_name`) onto `journey.next[]`; keep Path id in `later[]`. Reject duplicate module names in `next` (`400`). Return updated Journey document. |

### Merge rules

- Add methods as **`JourneyService` static methods** — do **not** keep a separate `JourneyPromoteService` class.
- Reuse existing helpers where identical: `_validate_object_id`, `_normalize_id`, `_check_permission(token, "mutate")` (replace local `_check_mutate_permission`).
- Port private helpers: `_path_id_in_later`, `_module_to_next_module`, `_module_name_in_next`, `_load_path_and_journey`.
- All MongoDB I/O via **`MongoIO`** convenience methods only.
- **Do not change** return shapes for existing mutation methods (`advance_resource`, `complete_resource`) or the new promote methods — all return plain Journey documents without embedded `profile`.

## Goals

- `JourneyService.promote_path_to_next` and `JourneyService.promote_module_to_next` match mentee API local behavior.
- Private promote helpers merged into `JourneyService`; no duplicate permission/validation utilities.
- Unit tests from mentee API ported to `tests/services/test_journey_service.py` (patch targets updated to `api_utils.services.journey_service.*`).
- Full test suite and build remain green.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run test tests/services/test_journey_service.py` — includes new promote coverage
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/journey_service.py` — add promote methods and helpers

- `tests/services/test_journey_service.py` — add ported promote tests

The agent must not update files outside this list.

## Execution Notes

- Merged promote helpers and public methods onto `JourneyService`; reused `_check_permission(token, "mutate")`.
- Ported 7 promote unit tests from mentee API with updated patch paths.
- `pipenv run test tests/services/test_journey_service.py`: 19 passed (journey tests); full suite 191 passed.
- `pipenv run build`: succeeded (`api_utils-0.5.1`).
