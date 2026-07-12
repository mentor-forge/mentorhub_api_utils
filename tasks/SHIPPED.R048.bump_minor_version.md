# R048 – Bump minor version before opening PR

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R047_export_services_public_api`  
**Description**: Bump the **minor** version of the `api-utils` package to reflect the new `api_utils.services` module before opening the harvest feature PR.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `README.md` (see "Release and publish")
- `pyproject.toml`
- `tasks/SHIPPED.R030.bump_patch_version.md` — prior bump pattern

At authoring time `version` is `0.3.0`. Adding a new `services/` package is a **minor** SemVer increment → `0.4.0`. If a prior task in this workflow already bumped the version, increment the **current minor** by one instead of hard-coding `0.4.0`.

## Goals

- `pyproject.toml` `version` bumped from `0.3.0` to `0.4.0` (minor only; do not change `MAJOR` unless instructed).
- No other `pyproject.toml` fields modified.
- Package builds with the new version string.

## Testing Expectations

- `pipenv run test`
- `pipenv run build` — artifact name reflects `0.4.0` (or current minor + 1)
- `pipenv run lint`

## Outputs

- `pyproject.toml` — `version` bump only

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
