# R042 – Harvest AggregationService into api_utils.services

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R041_harvest_note_service`  
**Description**: Move `AggregationService` from `mentorhub_mentee_api` into `api_utils.services.aggregation_service` with unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

- Source: `../mentorhub_mentee_api/src/services/aggregation_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_aggregation_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/SHIPPED.R010.add_resource_aggregation_collection_config.md`
- `../mentorhub_mentee_api/src/services/aggregation_service.py`
- `../mentorhub_mentee_api/test/services/test_aggregation_service.py`
- `api_utils/services/note_service.py` (harvested in R041)
- `api_utils/config/config.py` — `RESOURCE_AGGREGATION_COLLECTION_NAME`, `ROLE_MENTEE`

**AggregationService surface** (from mentee API):

- ISO 8601 duration helpers: `_parse_iso_duration`, `_format_iso_duration`, `_add_durations`
- `_find_aggregation` — primary lookup by `_id` (string of resource ObjectId), legacy fallback via `resource_id` match
- `get_aggregation_for_resource`, `get_aggregation_detail` (creates if missing)
- `add_hit` — any authenticated user; increments `hits`
- `add_completion` — requires `ROLE_MENTEE`; increments counters, optional rating/note/duration; creates Note via `NoteService.create_note` when `note` provided
- RBAC: `_check_permission` enforces mentee role for `add_completion`

**Import changes**:

- Replace `from src.services.note_service import NoteService` with `from api_utils.services.note_service import NoteService` (keep lazy import inside methods to avoid circular imports).

## Goals

- `api_utils.services.aggregation_service.AggregationService` matches mentee API behavior.
- Uses `config.RESOURCE_AGGREGATION_COLLECTION_NAME` directly (no `_collection_name()` fallback).
- All MongoDB I/O uses `MongoIO` convenience methods only.
- Unit tests ported to `tests/services/test_aggregation_service.py`.
- `api_utils/services/__init__.py` exports `AggregationService`.

## Testing Expectations

- `pipenv run test tests/services/test_aggregation_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/aggregation_service.py`
- `api_utils/services/__init__.py` — export `AggregationService`
- `tests/services/test_aggregation_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
