# R091 – Replace CodeArtifact release helpers with GitHub Release delivery

**Status**: Pending

**Type**: Feature

**Depends On**: R090

**Description**: Remove AWS/CodeArtifact and deliver versioned utils through GitHub — replace codeartifact release helpers with github release delivery.

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
- `scripts/publish-package`
- `scripts/tag-release`
- `Pipfile`
- `Pipfile.lock`

Source issue is authoritative for this migration. The agreed migration supersedes old CodeArtifact-auth prerequisites only in the paths explicitly migrated by these tasks; do not rewrite unrelated framework rules.

## Goals

- Keep build-package/build behavior compatible with Stage0 commands; replace AWS/twine upload behavior in publish-package with explicit GitHub Release asset upload that refuses to replace existing assets.
- Update tag-release messaging and guards: require version/tag agreement, intended main commit and a clean release state, reject moved/existing tags or duplicate assets; allow documented no-push preparation. Do not tag/push/publish while implementing this task.
- Use GitHub workflow or operator credentials only for publishing; building and consumer wheel downloads must work without them. Drop obsolete twine/CodeArtifact-only tools if unused, then regenerate locks from public PyPI.

### Craftsmanship Expectations

Keep package, auth and deployment ownership in the existing shared modules. Preserve APIs and runtime contracts unless the recorded migration decision explicitly requires a change; remove obsolete AWS auth knowledge rather than duplicate it. Keep every dependency reference reproducible.

## Testing Expectations

These checks are for future execution; none were run while creating this plan.

- Use temporary Git repos and mocked gh/network commands to check wrong-version/tag, existing-asset and failed-upload handling without changing real releases. Run pipenv run test, lint, build; inspect wheel/sdist and isolated wheel install.

## Outputs

- `scripts/publish-package`
- `scripts/tag-release`
- `Pipfile`
- `Pipfile.lock`
- `tests/release/test_release_helpers.py`

Only these implementation files may change. The orchestrator may also update/rename this task record under the established lifecycle.

## Execution boundary

This is a reviewable plan, not an execution record. Execute only this task's listed outputs when orchestration is separately authorized. Do not touch excluded MongoDB/Runbook utility repos, publish packages/tags, mutate issue/project state, or delete/provision AWS resources as a side effect. Future workflow publication happens only through the reviewed maintainer release path.

Where a task requires an unpublished release, an undecided production contract, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

System runtime decisions are coordinated in https://github.com/mentor-forge/mentorhub/issues/80. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Execution Notes

Reserved for the execution agent. No implementation, tests, service changes or publication have been performed.
