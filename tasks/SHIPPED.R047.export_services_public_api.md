# R047 – Export shared services from api_utils public API

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R046_harvest_journey_service`  
**Description**: Wire harvested service classes into the top-level `api_utils` package exports and document adoption for domain APIs.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/__init__.py`
- `api_utils/services/__init__.py`
- All harvested `api_utils/services/*_service.py` modules (R041–R046)

**External prerequisite**: Pending downstream refactor tasks in domain API repos (`mentorhub_mentee_api`, `mentorhub_mentor_api`, etc.) will switch `from src.services.X import X` to `from api_utils.services.X import X` (or `from api_utils import X` if re-exported). Those tasks are **out of scope** for this repo workflow.

## Goals

- `api_utils/__init__.py` re-exports all six service classes:
  - `NoteService`, `AggregationService`, `EventService`, `ResourceService`, `PathService`, `JourneyService`
- `__all__` updated to include the service exports alongside existing utilities.
- `README.md` documents:
  - `services/` package purpose
  - Import example: `from api_utils.services import JourneyService` or `from api_utils import JourneyService`
  - Note that domain APIs should depend on published `api-utils` package version after R048 bump, not copy `src/services/` locally

## Testing Expectations

- `pipenv run test` — full suite passes.
- `pipenv run build`
- Verify imports: `python -c "from api_utils import JourneyService, PathService; print(JourneyService, PathService)"`
- `pipenv run lint`

## Outputs

- `api_utils/__init__.py` — add service imports and `__all__` entries
- `api_utils/services/__init__.py` — finalize `__all__` listing all service classes
- `README.md` — services package documentation

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
