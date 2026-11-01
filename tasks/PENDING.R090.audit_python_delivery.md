# R090 – Audit package delivery and runtime AWS independence

**Status**: Pending

**Type**: Feature

**Depends On**: none

**Description**: Remove AWS/CodeArtifact and deliver versioned utils through GitHub — audit package delivery and runtime aws independence.

**Issue**: [I-UA01](https://github.com/mentor-forge/mentorhub_api_utils/issues/36)

## Path anchoring

All output paths are relative to this repository root. Sibling references are read-only context permitted by the repo planning guide.

## Context

- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md`
- `../mentorhub/DeveloperEdition/standards/sre_standards.md`
- `../mentorhub/DeveloperEdition/standards/api_standards.md`

Source issue is authoritative for this migration. The agreed migration supersedes old CodeArtifact-auth prerequisites only in the paths explicitly migrated by these tasks; do not rewrite unrelated framework rules.

## Goals

- Document current version 1.0.4 as a planning observation, existing build/Pipfile/tag/publish scripts, artifact contents and runtime coupling. Runtime search currently finds no boto3/Cognito provider integration in api_utils; verify instead of inventing a rewrite.
- Specify public Release wheel/sdist naming and exact Pipfile file URL consumption, hashes, Python 3.12 support and public PyPI transitives. Preserve api_utils import/distribution identity and public APIs.
- Record release/consumer order, rollback and version-gate requirements; no consumer or infrastructure edits in this repo.

### Craftsmanship Expectations

Keep package, auth and deployment ownership in the existing shared modules. Preserve APIs and runtime contracts unless the recorded migration decision explicitly requires a change; remove obsolete AWS auth knowledge rather than duplicate it. Keep every dependency reference reproducible.

## Testing Expectations

These checks are for future execution; none were run while creating this plan.

- Compare package metadata, source exports and lock sources; ensure the design never installs unrelated public PyPI api-utils.

## Outputs

- `docs/github-release-distribution.md`

Only these implementation files may change. The orchestrator may also update/rename this task record under the established lifecycle.

## Execution boundary

This is a reviewable plan, not an execution record. Execute only this task's listed outputs when orchestration is separately authorized. Do not touch excluded MongoDB/Runbook utility repos, publish packages/tags, mutate issue/project state, or delete/provision AWS resources as a side effect. Future workflow publication happens only through the reviewed maintainer release path.

Where a task requires an unpublished release, an undecided production contract, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

System runtime decisions are coordinated in https://github.com/mentor-forge/mentorhub/issues/80. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Execution Notes

Reserved for the execution agent. No implementation, tests, service changes or publication have been performed.
