# R040 – Scaffold api_utils.services package

**Status**: Pending  
**Type**: Feature  
**Depends On**: none  
**Description**: Create the `api_utils/services/` package skeleton and document the harvest workflow that lifts mentee API static service classes into shared library code.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Standards: `../mentorhub/DeveloperEdition/standards/api_standards.md`
- Source (read-only input): `../mentorhub_mentee_api/src/services/`
- In-repo: `README.md`, `api_utils/...`, `tests/...`, `tasks/...`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATION.md`
- `tasks/SHIPPED.R010.add_resource_aggregation_collection_config.md`
- `tasks/SHIPPED.R020.add_event_type_constants_config.md`

**Harvest source review** (`../mentorhub_mentee_api/src/services/`):

| Service | Class | Lines (approx.) | MongoIO | Cross-service deps |
|---------|-------|-----------------|---------|------------------|
| `note_service.py` | `NoteService` | 117 | ✓ | none |
| `aggregation_service.py` | `AggregationService` | 319 | ✓ | `NoteService` (lazy) |
| `event_service.py` | `EventService` | 85 | ✓ | `AggregationService` (lazy, link events) |
| `resource_service.py` | `ResourceService` | 228 | ✓ | `AggregationService`, `NoteService` (lazy) |
| `path_service.py` | `PathService` | 148 | ✓ | `ResourceService` (lazy) |
| `journey_service.py` | `JourneyService` | 378 | ✓ | `EventService`, `AggregationService` (lazy) |

**Dependency harvest order** (R041–R046): Note → Aggregation → Event → Resource → Path → Journey.

**External prerequisite**: Domain API repos (`mentorhub_mentee_api`, `mentorhub_mentor_api`, etc.) have **separate pending tasks** to refactor routes and thin service wrappers to import from `api_utils.services`. This workflow does **not** modify any domain API repository.

**MongoDB I/O rule**: Harvested services must continue routing all MongoDB access through `MongoIO` — no direct PyMongo `collection.find` / `find_one` calls.

## Goals

- `api_utils/services/` package exists with `__init__.py` ready to re-export service classes as they are harvested in R041–R046.
- Package docstring documents that these are shared domain service implementations sourced from `mentorhub_mentee_api`, and that domain APIs should import from `api_utils.services` rather than maintaining duplicate `src/services/` copies.
- `README.md` **Project Structure** section lists the new `services/` package.
- No service implementation files are added in this task — scaffold only.

## Testing Expectations

- `pipenv run test` — all existing tests pass (no behavioral change expected).
- `pipenv run build` — package builds and includes the new `api_utils.services` namespace.
- `pipenv run lint` — no new linter errors.

## Outputs

- `api_utils/services/__init__.py` — package init (empty `__all__` or placeholder comment until R047)
- `README.md` — add `services/` to Project Structure

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
