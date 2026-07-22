# R140 – Bump minor version before opening PR

**Status**: Pending  
**Task Type**: Chore  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Bump the **minor** version of the `api_utils` package before opening the pull
request for the harvest feature, per the repo release process ("make sure to
bump version in `pyproject.toml` before opening PR"). This is the release the
Mentor API repos will pin to (see
`mentorhub_mentor_api/tasks/ISSUE.mentorhub_mentor_api.bump_api_utils_dependency.md`).

## Context / Input files

- `mentorhub_api_utils/README.md` (see "Release and publish")
- `mentorhub_api_utils/pyproject.toml`
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`

## Requirements

- Bump the **minor** segment to the next minor beyond the harvested baseline —
  target **`0.6.0`** (the harvest baseline is the published `0.5.x` line
  reconciled in R040).
  - If R040 landed a different baseline patch, still target the next minor
    (`0.6.0`), not a patch bump.
- Do not change `MAJOR`; reset `PATCH` to `0` for the new minor.
- Do not modify any other field in `pyproject.toml`.
- One bump for the whole feature (R040–R130) in a single PR — do not bump
  per task.
- Publication to CodeArtifact happens after merge via `pipenv run tag-release`
  (out of scope for this task; note it in the PR).

## Files to modify

- **Modify**: `pyproject.toml` — `version = "0.2.4"` → `version = "0.6.0"`
  (next minor beyond the reconciled `0.5.x` baseline).

## Testing expectations

- `pipenv run test` — package still builds/imports cleanly with the new version.
- `pipenv run lint` clean.
- `pipenv run build` — build succeeds and reflects the new version
  (`api_utils-0.6.0*`).

## Packaging / build checks

- `pipenv run build` produces the `0.6.0` sdist/wheel.
- Confirm no new linter errors.

## Dependencies / Ordering

- Must run **after R040–R130**. Final task before the feature PR.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Confirmed R040–R130 complete.
- [ ] Bumped `version` to the next minor (`0.6.0`).
- [ ] `pipenv run test` / `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.
- [ ] Opened the feature PR (publish via `pipenv run tag-release` after merge).

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent)_
