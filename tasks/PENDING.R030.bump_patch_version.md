# R030 – Bump patch version before opening PR

**Status**: Pending  
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

- [ ] Reviewed all **Context / Input files**.
- [ ] Confirmed R010 and R020 are complete.
- [ ] Bumped only the patch segment of `version` in `pyproject.toml`.
- [ ] Ran unit tests (`pipenv run test`); all passing.
- [ ] Ran packaging/build steps (`pipenv run build`); build successful.
- [ ] Created a scoped commit referencing this task ID.
- [ ] Opened the pull request for the feature.

## Implementation notes (to be updated by the agent)

**Summary of changes**
- _e.g., "Bumped version 0.2.3 -> 0.2.4 in pyproject.toml."_

**Testing results**
- Unit tests: _command(s) run, high‑level outcome_
- Packaging/build: _command(s) run, high‑level outcome_

**Follow‑up tasks**
- _none expected_
