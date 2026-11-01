# R092 – Add AWS-free PR validation and tag-triggered Release workflow

**Status**: Pending

**Type**: Feature

**Depends On**: R091

**Description**: Remove AWS/CodeArtifact and deliver versioned utils through GitHub — add aws-free pr validation and tag-triggered release workflow.

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
- `.github/workflows/publish-package.yml`

Source issue is authoritative for this migration. The agreed migration supersedes old CodeArtifact-auth prerequisites only in the paths explicitly migrated by these tasks; do not rewrite unrelated framework rules.

## Goals

- Replace AWS credential/OIDC and twine upload steps in publish-package.yml with test/build/version checks and a GitHub Release containing the already-tested wheel/sdist plus hashes.
- Use contents: read for checks and contents: write only for publication, no id-token: write or AWS secrets. Ensure public visibility through the public repo, stop on an existing release/asset rather than replacing content.
- Add separate PR validation that installs from committed public locks, tests and builds without publishing. Verify actual built artifacts rather than only source checkout imports.

### Craftsmanship Expectations

Keep package, auth and deployment ownership in the existing shared modules. Preserve APIs and runtime contracts unless the recorded migration decision explicitly requires a change; remove obsolete AWS auth knowledge rather than duplicate it. Keep every dependency reference reproducible.

## Testing Expectations

These checks are for future execution; none were run while creating this plan.

- Lint workflows; run pipenv run test, lint, build and inspect package contents. Dry-run publication with mocked/test fixtures; actual tag workflow evidence is a post-merge maintainer gate, not permission to publish now.

## Outputs

- `.github/workflows/publish-package.yml`
- `.github/workflows/ci.yml`
- `docs/github-release-distribution.md`

Only these implementation files may change. The orchestrator may also update/rename this task record under the established lifecycle.

## Execution boundary

This is a reviewable plan, not an execution record. Execute only this task's listed outputs when orchestration is separately authorized. Do not touch excluded MongoDB/Runbook utility repos, publish packages/tags, mutate issue/project state, or delete/provision AWS resources as a side effect. Future workflow publication happens only through the reviewed maintainer release path.

Where a task requires an unpublished release, an undecided production contract, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

System runtime decisions are coordinated in https://github.com/mentor-forge/mentorhub/issues/80. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Execution Notes

Reserved for the execution agent. No implementation, tests, service changes or publication have been performed.
