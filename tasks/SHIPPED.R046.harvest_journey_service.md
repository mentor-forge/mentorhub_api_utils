# R046 – Harvest JourneyService into api_utils.services

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R045_harvest_path_service`  
**Description**: Move `JourneyService` from `mentorhub_mentee_api` into `api_utils.services.journey_service` with unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

- Source: `../mentorhub_mentee_api/src/services/journey_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_journey_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/SHIPPED.R020.add_event_type_constants_config.md`
- `../mentorhub_mentee_api/src/services/journey_service.py`
- `../mentorhub_mentee_api/test/services/test_journey_service.py`
- `api_utils/services/event_service.py`
- `api_utils/services/aggregation_service.py`
- `api_utils/config/config.py` — `ROLE_MENTEE`, `EVENT_TYPE_ADVANCED`, `EVENT_TYPE_COMPLETED`, `JOURNEY_COLLECTION_NAME`, `RESOURCE_COLLECTION_NAME`

**JourneyService surface** (mentee API — full mentee journey lifecycle):

- Constants: `TEMPLATE_JOURNEY_ID = "ffff00000000000000000001"`, `RESTRICTED_UPDATE_FIELDS`
- RBAC: `_check_permission` — read (open), update (owner `profile_id` or admin), mutate (requires `profile_id`), complete (requires `ROLE_MENTEE`)
- `get_my_journey` — get-or-create from template clone (`_clone_template`)
- `get_journey`, `create_journey`, `update_journey`
- `advance_resource` — moves resource from `next` to `now`; creates `EVENT_TYPE_ADVANCED` event
- `complete_resource` — moves from `now` to `library`; calls `AggregationService.add_completion` and `EventService.create_event` with `EVENT_TYPE_COMPLETED`
- Scope helpers: `_resource_id_in_next`, `_remove_resource_from_next`, `_find_now_entry`, `_event_token`

**Import changes**:

- Replace `from src.services.event_service import EventService` and `from src.services.aggregation_service import AggregationService` with `api_utils.services.*` (lazy imports inside `advance_resource` and `complete_resource`).

**Note**: `mentorhub_mentor_api` `JourneyService` is read-only (resource counts for dashboard, mentor/admin RBAC). Downstream refactor will keep mentor-specific logic local or as a thin wrapper over shared helpers.

## Goals

- `api_utils.services.journey_service.JourneyService` matches mentee API behavior including template clone, advance, and complete flows.
- All MongoDB I/O uses `MongoIO` convenience methods.
- Unit tests ported to `tests/services/test_journey_service.py` (get-or-create, advance, complete, RBAC).
- `api_utils/services/__init__.py` exports `JourneyService` and `TEMPLATE_JOURNEY_ID` if tests import it.

## Testing Expectations

- `pipenv run test tests/services/test_journey_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/journey_service.py`
- `api_utils/services/__init__.py` — export `JourneyService`
- `tests/services/test_journey_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
