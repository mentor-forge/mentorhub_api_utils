# R066 – Export harvested services and bump minor version to 0.6.0

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R065_harvest_encounter_and_profile_services`  
**Description**: Export the four newly harvested services from the `api_utils.services` public API, refresh service docs, and bump `pyproject.toml` from `0.5.2` to `0.6.0` so domain APIs can pin and install the full shared service surface from CodeArtifact after merge and `tag-release`. This is the release task for the Mentor-API harvest feature.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — **Release and publish**; version pin examples referencing `0.5.2`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R047.export_services_public_api.md` — prior services-export pattern
- `tasks/SHIPPED.R054.bump_minor_version_list_query.md` — prior **minor** bump pattern
- `pyproject.toml` — current `version` (expected `0.5.2` at planning time)
- `api_utils/services/__init__.py` — current exports (Aggregation, Event, Journey, Note, Path, Resource)

### Versioning

- This is a **minor** release: additive new services (`PlanService`, `MenteeService`, `EncounterService`, `ProfileService`) and one additive `JourneyService` method; backward-compatible for existing consumers.
- At planning time `pyproject.toml` has `version = "0.5.2"` → bump to **`0.6.0`**.
- If another bump landed first, increment the **current** minor by one rather than hard-coding `0.6.0`. Do not change `MAJOR`.

Publishing to CodeArtifact happens after PR merge via `pipenv run tag-release` (orchestrator reminds the developer). Do not publish from this task.

## Goals

- `api_utils/services/__init__.py` imports and re-exports `PlanService`, `MenteeService`, `EncounterService`, `ProfileService`, and adds each to `__all__` (alongside the existing services).
- `import api_utils.services as s; s.PlanService/…/s.ProfileService` all resolve.
- `README.md` documents the new shared services and updates any `api-utils==0.5.2` pin examples to `0.6.0`.
- `pyproject.toml` `version` is `0.6.0` (or next minor).

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db`
- `pipenv run test` — full suite green with all harvested services
- `pipenv run lint`
- `pipenv run build` — artifact name/version reflects the new minor (e.g. `api_utils-0.6.0-...`)

## Outputs

- `api_utils/services/__init__.py` — export the four new services
- `pyproject.toml` — bump `version` minor segment
- `README.md` — document new services; update documented `api-utils` pin

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
