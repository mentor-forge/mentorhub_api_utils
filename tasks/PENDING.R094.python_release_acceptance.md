# R094 – Verify release consumption and hand off to API consumers

**Status**: Pending

**Type**: Feature

**Depends On**: R093

**Description**: Remove AWS/CodeArtifact and deliver versioned utils through GitHub — verify release consumption and hand off to api consumers.

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

- Prepare a clean external consumer fixture which installs the wheel at its exact release URL through Pipenv, locks hashes and syncs without AWS CLI/token/index. Confirm third-party packages use public PyPI.
- After maintainer publication, record the actual release URL, tag commit, package version, hash and clean install evidence. Until publication exists, record a stop gate instead of fabricating successful downloads.
- Preserve Config/auth/services exports and run unit/integration/e2e packaging gates as applicable with non-AWS local backing services. This task makes no sibling-repo edits.

### Craftsmanship Expectations

Keep package, auth and deployment ownership in the existing shared modules. Preserve APIs and runtime contracts unless the recorded migration decision explicitly requires a change; remove obsolete AWS auth knowledge rather than duplicate it. Keep every dependency reference reproducible.

## Testing Expectations

These checks are for future execution; none were run while creating this plan.

- pipenv run test, lint, build; run pipenv run integration and pipenv run e2e with the documented local backing environment. Install actual published wheel in a clean temporary consumer and verify import path, version and expected exports. External prerequisite: release published after review/merge.

## Outputs

- `docs/github-release-distribution.md`
- `tests/release/test_wheel_contents.py`

Only these implementation files may change. The orchestrator may also update/rename this task record under the established lifecycle.

## Execution boundary

This is a reviewable plan, not an execution record. Execute only this task's listed outputs when orchestration is separately authorized. Do not touch excluded MongoDB/Runbook utility repos, publish packages/tags, mutate issue/project state, or delete/provision AWS resources as a side effect. Future workflow publication happens only through the reviewed maintainer release path.

Where a task requires an unpublished release, an undecided production contract, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

System runtime decisions are coordinated in https://github.com/mentor-forge/mentorhub/issues/80. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Execution Notes

Reserved for the execution agent. No implementation, tests, service changes or publication have been performed.
