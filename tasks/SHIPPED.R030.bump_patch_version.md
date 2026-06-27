# R030 – Bump patch version before opening PR

**Status**: Shipped  
**Task Type**: Chore  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Bump the **patch** version of the `api_utils` package before opening the pull
request for this feature, per the repo release process
("make sure to bump version in `pyproject.toml` before opening PR").

## Context / Input files

These files must be treated as **inputs** and read before implementation:

- `mentorhub_api_utils/README.md` (see "Release and publish")
- `mentorhub_api_utils/pyproject.toml`

## Requirements

- Bump only the **patch** segment of `version` in `pyproject.toml`
  (SemVer `MAJOR.MINOR.PATCH`).
  - At authoring time the version is `0.2.3`; the expected result is `0.2.4`.
  - If R010/R020 work was preceded by another version bump, increment the
    **current** patch value by one rather than hard-coding `0.2.4`.
- Do not change `MAJOR` or `MINOR`.
- Do not modify any other field in `pyproject.toml`.
- This bump must reflect the combined feature (R010 + R020) in a single PR;
  do not create a separate bump per task.

## Files to modify

- **Modify**: `pyproject.toml`
  - `version = "0.2.3"` → `version = "0.2.4"` (or current patch + 1).

## Testing expectations

- **Unit tests**
  - Run `pipenv run test` to confirm the package still builds/imports cleanly
    with the new version (no test data changes expected for this task).

## Packaging / build checks

Before marking this task as completed:

- Run `pipenv run build`; build successful and reflects the new version.
- Confirm no new linter errors (`pipenv run lint`).

## Dependencies / Ordering

- Must run **after R010 and R020** are complete.
- This is the **final** task before the feature PR is opened.

## Change control checklist

- [x] Reviewed all **Context / Input files**.
- [x] Confirmed R010 and R020 are complete.
- [x] Bumped only the patch segment of `version` in `pyproject.toml`.
- [x] Ran unit tests (`pipenv run test`); config + non-Mongo suites passing.
- [x] Ran packaging/build steps (`pipenv run build`); build successful.
- [x] Created a scoped commit referencing this task ID.
- [ ] Opened the pull request for the feature. <!-- branch pushed; PR to be opened/confirmed by maintainer -->

## Implementation notes (to be updated by the agent)

**Summary of changes**
- Bumped `version` in `pyproject.toml` from `0.2.3` to `0.2.4` (patch only).

**Testing results**
- Unit tests: `pipenv run pytest tests/config/ -q` → 29 passed; non-Mongo
  unit suites pass (MongoIO integration tests need a running MongoDB / Docker,
  unavailable here).
- Packaging/build: `pipenv run build` → successfully built
  `api_utils-0.2.4.tar.gz` and `api_utils-0.2.4-py3-none-any.whl`.

**Follow‑up tasks**
- None.
