# R089 – Bump api-utils patch to 1.0.1

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R088_rename_token_name_to_display_name`  
**Description**: Publish F-AA04’s token `display_name` change as patch **`1.0.1`** so `mentorhub_admin_api` can pin and install it from CodeArtifact after merge and `tag-release`.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — **Release and publish**; pin examples and **Downstream planning artifacts** still saying `api-utils==1.0.0`
- `pyproject.toml` — current `version` (expected `1.0.0` at planning time)
- `tasks/SHIPPED.R058.bump_patch_resource_list_filters.md` — patch-bump pattern
- `tasks/PENDING.R088.rename_token_name_to_display_name.md`
- `tasks/ISSUE.mentorhub_admin_api.pin_1_0_1_display_name.md` — downstream only; do not execute
- GitHub: https://github.com/mentor-forge/mentorhub_admin_api/issues/8

### Versioning

- This is a **patch** release: token dict key rename (`name` → `display_name`). Pre-MVP breaking change on the flask-token dict; issue F-AA04 names the consumer pin **`1.0.1`**.
- At planning time `pyproject.toml` has `version = "1.0.0"` → bump to **`1.0.1`**.
- If another bump landed first, increment the **current** patch by one rather than hard-coding `1.0.1`, and record the actual version in Execution Notes. Prefer **`1.0.1`** so it matches the GitHub issue.
- Do not change `MAJOR` or `MINOR`.

Publishing to CodeArtifact happens after PR merge via `pipenv run tag-release` (orchestrator reminds the developer). Do not publish from this task.

### Downstream (out of scope — other repos)

After publish, `mentorhub_admin_api` consumes this release via:

- `tasks/ISSUE.mentorhub_admin_api.pin_1_0_1_display_name.md`

Do **not** orchestrate Admin API (or other domain API) changes from this repo.

## Goals

- `pyproject.toml` `version` is `1.0.1` (or next patch if already bumped).
- `README.md` pin examples that still say `api-utils==1.0.0` are updated to `api-utils==1.0.1`, including **Release and publish** and **Downstream planning artifacts**.
- README notes in one sentence that `create_flask_token()` returns `display_name` (not `name`); keep the edit short.
- No further token or service behavior changes in this task.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run test`
- `pipenv run lint` — R089 files `black`-clean (repo-wide lint may fail on pre-existing files)
- `pipenv run build` — artifact name/version reflects the new patch (e.g. `api_utils-1.0.1-...`)

## Outputs

- `pyproject.toml` — bump `version` patch segment only
- `README.md` — pin examples + brief `display_name` note; keep edits minimal

The agent must not update files outside this list.

## Execution Notes
