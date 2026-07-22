# R130 – Export shared services + update docs

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Finalize the public surface of the harvested/extended services and document
them, so domain APIs can import the full Resource/Event/Path/Journey/Plan/
Encounter/Mentee/Profile domains from `api_utils.services`.

## Context / Input files

- `mentorhub_api_utils/api_utils/services/__init__.py` (assembled across R040–R120)
- `mentorhub_api_utils/api_utils/__init__.py`
- `mentorhub_api_utils/README.md` ("Project Structure")
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- `api_utils/services/__init__.py` exports every service and its list spec:
  `ResourceService` (+ `RESOURCE_LIST_FILTERS`/`_ORDER`), `EventService`
  (+ `EVENT_LIST_FILTERS`/`_ORDER`), `PathService` (+ `PATH_LIST_FILTERS`/
  `_ORDER`), `JourneyService`, `PlanService` (+ `PLAN_LIST_FILTERS`/`_ORDER`),
  `EncounterService`, `MenteeService`, `ProfileService`.
- Re-export from the package root (`api_utils/__init__.py`) as appropriate and
  keep `__all__` accurate.
- Update `README.md` "Project Structure" to list the `services/` package and the
  domains it ships. Update any service docs under `docs/` if present.
- No behavior changes in this task — packaging/export/docs only.

## Files to modify / create

- **Modify**: `api_utils/services/__init__.py`
- **Modify**: `api_utils/__init__.py`
- **Modify**: `README.md`
- **Modify**: `docs/` service documentation (if applicable)

## Testing expectations

- `pipenv run test` green (no behavior change expected).
- `pipenv run lint` and `pipenv run build` clean.
- Import smoke test: `from api_utils.services import (ResourceService,
  EventService, PathService, JourneyService, PlanService, EncounterService,
  MenteeService, ProfileService)` succeeds.

## Packaging / build checks

- All suites pass; version bump handled in **R140**.

## Dependencies / Ordering

- **Depends On**: R050–R120 (all services present). Must run **before R140**.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Exported all services + specs from `api_utils.services`.
- [ ] Updated package-root re-exports and `__all__`.
- [ ] Updated `README.md` (+ docs) to list shared services.
- [ ] `pipenv run test` / `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
