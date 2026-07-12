# R043 – Harvest EventService into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R042_harvest_aggregation_service`  
**Description**: Move `EventService` from `mentorhub_mentee_api` into `api_utils.services.event_service` with unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

- Source: `../mentorhub_mentee_api/src/services/event_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_event_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/SHIPPED.R020.add_event_type_constants_config.md`
- `../mentorhub_mentee_api/src/services/event_service.py`
- `../mentorhub_mentee_api/test/services/test_event_service.py`
- `api_utils/services/aggregation_service.py`

**EventService surface** (mentee API — POST-only contract):

- `create_event(data, token, breadcrumb)` — strips client `_id`, `context`, `created`; sets `context` from token; encodes `ID_PROPERTIES` (`_id`, `profile_id`, `resource_id`, `journey_id`); sets `created` breadcrumb
- On `type == "link"` (compare against `config.EVENT_TYPE_LINK`): calls `AggregationService.add_hit` when `token.resource_id` is present
- Auth-only `_check_permission` placeholder

**Import changes**:

- Replace `from src.services.aggregation_service import AggregationService` with `from api_utils.services.aggregation_service import AggregationService` (lazy import inside `create_event`).

**Note**: `mentorhub_mentor_api` retains a broader `EventService` (list/get with infinite scroll). Downstream refactor tasks will decide whether mentor API keeps a local wrapper or extends the shared service. Harvest the **mentee** implementation as canonical for the shared library.

## Goals

- `api_utils.services.event_service.EventService` matches mentee API `create_event` behavior including link→`add_hit` side effect.
- Uses `config.EVENT_TYPE_LINK` constant (not hard-coded `"link"` string if config defines it).
- Unit tests ported to `tests/services/test_event_service.py`.
- `api_utils/services/__init__.py` exports `EventService`.

## Testing Expectations

- `pipenv run test tests/services/test_event_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/event_service.py`
- `api_utils/services/__init__.py` — export `EventService`
- `tests/services/test_event_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
