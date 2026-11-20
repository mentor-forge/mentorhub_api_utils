# R091 – Replace CodeArtifact release helpers with GitHub Release delivery

**Status**: Shipped

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

Where a task requires an unpublished release, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

The cloud-agnostic local deployment boundary is coordinated in https://github.com/mentor-forge/mentorhub/issues/80; production provider selection does not gate this release. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Cloud-agnostic deployment boundary

The deliverable is a cloud-agnostic **local** deployment plus the agreed GitHub dependency/build migration. Existing identity/hosting implementations are largely placeholders: audit actual executable dependencies before proposing changes. Selecting, implementing or migrating to a production IdP/hosting provider is not a prerequisite for library releases, journey package/build/CI changes or local acceptance.

Keep application-facing backing-service contracts and environment settings provider neutral. Concentrate necessary integration changes in Admin API and DeveloperEdition/docker-compose.yaml where inspection proves coupling; preserve the existing shared JWT/redirect contracts and local persona/mocked-service behavior. Do not create per-journey provider adapters, new identity schemas or a general multi-cloud framework speculatively.

Cloud-specific provisioning, backing-service configuration, identity-provider wiring, roles/secrets and deployment overlays belong to the relevant infrastructure repo: mentorhub_cloudformation owns AWS, including future CodeArtifact provisioning. Future separate repos may implement Google, Microsoft/Azure, IBM or Red Hat platforms against the same contracts; do not create or implement them in this effort. Core compose must not require AWS accounts, credentials or endpoints. A locally optional emulator is not a live AWS dependency; retain it only if useful without making it a required cloud-specific integration.

AWS inventory, secure backup/restore evidence and separately approved decommissioning remain I-S01 responsibilities. Production provider selection or a live production cutover is future infrastructure/integration work, not an acceptance gate for the cloud-agnostic local stack.

## Execution Notes

- Replaced the operator upload with a GitHub Release upload of the exact matching prebuilt wheel, source archive, and generated SHA-256 manifest. It checks the local and remote tag commits and refuses to upload to a release with existing assets. The tag helper requires a clean checkout of the exact remote main commit, verifies existing tags and releases, and retains `--no-push` for local preparation.
- Removed Twine and its now-unused development dependencies from the public PyPI lock while retaining unrelated pins. `pipenv verify` and `pipenv sync --dev` passed.
- `pipenv run test` passed 258 tests, including four release-helper tests using temporary Git repositories and a mocked GitHub CLI. Lint and the isolated artifact build passed. The built wheel and source archive have the expected 1.0.4 filenames and distribution contents.
- The locally built wheel installed in a clean Python 3.12 environment and passed `pip check`. Its import reproduced the pre-existing missing PyJWT metadata noted in R090. R093 owns the metadata fix and a fresh isolated import check. No actual tag, release, or asset was created.
