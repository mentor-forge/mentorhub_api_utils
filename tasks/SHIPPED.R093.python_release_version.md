# R093 – Prepare the next Python utils version and adoption documentation

**Status**: Shipped

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

Where a task requires an unpublished release, unavailable live schema or operator evidence, stop execution at that prerequisite and report it; do not guess values or substitute the unrelated PyPI api-utils package. Pending status describes the plan's review state, not proof that external execution gates are satisfied.

## External prerequisites

The cloud-agnostic local deployment boundary is coordinated in https://github.com/mentor-forge/mentorhub/issues/80; production provider selection does not gate this release. Consumer cutover follows the maintainer-authorized publication of this repo's release; editing consumer repos is outside this plan.

## Cloud-agnostic deployment boundary

The deliverable is a cloud-agnostic **local** deployment plus the agreed GitHub dependency/build migration. Existing identity/hosting implementations are largely placeholders: audit actual executable dependencies before proposing changes. Selecting, implementing or migrating to a production IdP/hosting provider is not a prerequisite for library releases, journey package/build/CI changes or local acceptance.

Keep application-facing backing-service contracts and environment settings provider neutral. Concentrate necessary integration changes in Admin API and DeveloperEdition/docker-compose.yaml where inspection proves coupling; preserve the existing shared JWT/redirect contracts and local persona/mocked-service behavior. Do not create per-journey provider adapters, new identity schemas or a general multi-cloud framework speculatively.

Cloud-specific provisioning, backing-service configuration, identity-provider wiring, roles/secrets and deployment overlays belong to the relevant infrastructure repo: mentorhub_cloudformation owns AWS, including future CodeArtifact provisioning. Future separate repos may implement Google, Microsoft/Azure, IBM or Red Hat platforms against the same contracts; do not create or implement them in this effort. Core compose must not require AWS accounts, credentials or endpoints. A locally optional emulator is not a live AWS dependency; retain it only if useful without making it a required cloud-specific integration.

AWS inventory, secure backup/restore evidence and separately approved decommissioning remain I-S01 responsibilities. Production provider selection or a live production cutover is future infrastructure/integration work, not an acceptance gate for the cloud-agnostic local stack.

## Execution Notes

- Local tags ended at v1.0.4. GitHub returned no matching tag and no release for v1.0.5. Prepared 1.0.5 and added PyJWT to the wheel runtime dependencies.
- Updated adoption, lockfile, checksum, rollback floor, and maintainer publication instructions. The documented public wheel URL becomes usable only after publication.
- Passed 258 unit tests, Black formatting check, isolated wheel and sdist builds, and clean Python 3.12 wheel installation with public PyPI transitives. Pip reported no broken requirements and imports of Config, authentication, and services resolved from the clean environment.
- No tags, releases, or consumer pin changes were made.
