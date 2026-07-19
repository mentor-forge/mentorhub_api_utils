# R058 – Bump api-utils patch for Resource list filter extension

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R057_test_resource_list_multi_field_filters`  
**Description**: Bump `api-utils` patch version to `0.5.1` so domain APIs can pin and install the extended `RESOURCE_LIST_FILTERS` from CodeArtifact after merge and `tag-release`.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md` — **Release and publish**; any version pin examples referencing `0.5.0`
- `pyproject.toml` — current `version` (expected `0.5.0` at planning time)
- `tasks/SHIPPED.R054.bump_minor_version_list_query.md` — prior version-bump pattern
- `tasks/SHIPPED.R030.bump_patch_version.md` — patch-bump checklist precedent
- `tasks/PENDING.R056.extend_resource_list_filters.md`
- `tasks/PENDING.R057.test_resource_list_multi_field_filters.md`

### Versioning

- This is a **patch** release: additive, backward-compatible filter keys on an existing constant.
- At planning time `pyproject.toml` has `version = "0.5.0"` → bump to **`0.5.1`**.
- If another bump landed first, increment the **current** patch by one rather than hard-coding `0.5.1`.
- Do not change `MAJOR` or `MINOR`.

Publishing to CodeArtifact happens after PR merge via `pipenv run tag-release` (orchestrator reminds the developer). Do not publish from this task.

### Downstream (out of scope — other repos)

After publish, `mentorhub_mentee_api` consumes this release via existing tasks:

- `PENDING.L190.bump_api_utils_resource_list_filters.md`
- `PENDING.L191.document_resource_list_multi_field_filters.md`
- `PENDING.L192.test_resource_list_multi_field_filters.md`

## Goals

- `pyproject.toml` `version` is the next patch (expected `0.5.1`).
- `README.md` version pin examples that still say `api-utils==0.5.0` (or equivalent) are updated to the new patch so consumers copy the current pin.
- No further code or filter behavior changes in this task.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- **Unit tests**
  - `pipenv run test`
- **Lint / build**
  - `pipenv run lint`
  - `pipenv run build` — artifact name/version reflects the new patch (e.g. `api_utils-0.5.1-...`)

## Outputs

- `pyproject.toml` — bump `version` patch segment only
- `README.md` — update documented `api-utils` pin / changelog mention for the new Resource list filters if present; keep edits minimal

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
