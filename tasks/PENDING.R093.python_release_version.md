# R093 – Prepare the next Python utils version and adoption documentation

**Status**: Pending

**Type**: Feature

**Depends On**: R092

**Description**: Remove AWS/CodeArtifact and deliver versioned utils through GitHub — prepare the next python utils version and adoption documentation.

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
- `pyproject.toml`

Source issue is authoritative for this migration. The agreed migration supersedes old CodeArtifact-auth prerequisites only in the paths explicitly migrated by these tasks; do not rewrite unrelated framework rules.

## Goals

- Bump the current patch to the next unused version after re-reading metadata/tags; 1.0.5 is a candidate from observed 1.0.4, not a promise that it is available. Do not change major/minor for delivery-only work.
- Update README install/release instructions, exact wheel URL/hashes and Pipenv locking example, public transitives and rollback. Update only stale dependency-auth guidance in tasks/_PLANNING.md.
- Record maintainer merge → permanent matching tag → tested release publication handoff. Do not edit consumer pins, create tags, push or publish as part of task execution.

### Craftsmanship Expectations

Keep package, auth and deployment ownership in the existing shared modules. Preserve APIs and runtime contracts unless the recorded migration decision explicitly requires a change; remove obsolete AWS auth knowledge rather than duplicate it. Keep every dependency reference reproducible.

## Testing Expectations

These checks are for future execution; none were run while creating this plan.

- pipenv run test, lint and build; check metadata/version and artifact names agree. Test isolated import without source-tree masking. Review no stale mandatory CodeArtifact auth in active instructions.

## Outputs

- `pyproject.toml`
- `README.md`
- `docs/github-release-distribution.md`
- `tasks/_PLANNING.md`

Only these implementation files may change. The orchestrator may also update/rename this task record under the established lifecycle.

## Execution boundary

This is a reviewable plan, not an execution record. Execute only this task's listed outputs when orchestration is separately authorized. Do not touch excluded MongoDB/Runbook utility repos, publish packages/tags, mutate issue/project state, or delete/provision AWS resources as a side effect. Future workflow publication happens only through the reviewed maintainer release path.

Where a task requires an unpublished release, an undecided production contract, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

System runtime decisions are coordinated in https://github.com/mentor-forge/mentorhub/issues/80. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Execution Notes

Reserved for the execution agent. No implementation, tests, service changes or publication have been performed.
