# R061 – Bump api-utils patch for Journey promote and GET detail harvest

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R060_harvest_journey_get_my_journey_detail`  
**Description**: Bump `api-utils` patch version to `0.5.2` so domain APIs can pin and install Journey promote mutations and `get_my_journey_detail` from CodeArtifact after merge and `tag-release`.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — **Release and publish**; any version pin examples referencing `0.5.1`
- `pyproject.toml` — current `version` (expected `0.5.1` at planning time)
- `tasks/SHIPPED.R058.bump_patch_resource_list_filters.md` — prior patch-bump pattern
- `tasks/SHIPPED.R059.harvest_journey_promote_mutations.md`
- `tasks/SHIPPED.R060.harvest_journey_get_my_journey_detail.md`

### Versioning

- This is a **patch** release: additive methods on existing `JourneyService`; backward-compatible for consumers that do not call the new APIs.
- At planning time `pyproject.toml` has `version = "0.5.1"` → bump to **`0.5.2`**.
- If another bump landed first, increment the **current** patch by one rather than hard-coding `0.5.2`.
- Do not change `MAJOR` or `MINOR`.

Publishing to CodeArtifact happens after PR merge via `pipenv run tag-release` (orchestrator reminds the developer). Do not publish from this task.

### Downstream (out of scope — other repos)

After publish, domain APIs consume this release via:

- `tasks/ISSUE.mentorhub_mentee_api.adopt_journey_harvest_from_api_utils.md`
- `tasks/ISSUE.mentorhub_mentor_api.bump_api_utils_journey_harvest.md`

## Goals

- `pyproject.toml` `version` is the next patch (expected `0.5.2`).
- `README.md` version pin examples that still say `api-utils==0.5.1` (or equivalent) are updated to the new patch.
- No further Journey service behavior changes in this task.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run test`
- `pipenv run lint`
- `pipenv run build` — artifact name/version reflects the new patch (e.g. `api_utils-0.5.2-...`)

## Outputs

- `pyproject.toml` — bump `version` patch segment only
- `README.md` — update documented `api-utils` pin if present; keep edits minimal

The agent must not update files outside this list.

## Execution Notes

- Bumped `pyproject.toml` `0.5.1` → `0.5.2`; updated README pin example.
- `pipenv run test`: 196 passed; `pipenv run build`: `api_utils-0.5.2` sdist + wheel.
