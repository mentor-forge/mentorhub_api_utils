# Bump api-utils pin after Journey promote + GET detail harvest

> **Cross-repo issue artifact.** Paste-ready description for follow-on planning
> in **`mentorhub_mentor_api`**. Not part of the current `PENDING.*`
> orchestration chain in `mentorhub_api_utils` and must not be executed from
> that folder.
> **Blocked on**: `mentorhub_api_utils` R059–R061 shipped and published to
> CodeArtifact (`api-utils>=0.5.2`).

## Summary

The Mentor API does **not** use Journey promote mutations or GET profile
enrichment today — its local `src/services/journey_service.py` exposes only
mentor-specific `get_journey_progress` for the dashboard. After the upstream
harvest ships, bump the shared library pin so this repo stays on the current
`api-utils` release and picks up any shared fixes bundled with the Journey
harvest.

## Scope

### Dependency bump

- Pin `api-utils` to **`0.5.2`** (or the patch release that includes R059–R061)
  in `Pipfile` / `Pipfile.lock`.
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed).

### No route or local service changes required

- Do **not** adopt `get_my_journey_detail` or promote methods in the Mentor API
  unless a future feature requires them.
- Keep local `JourneyService.get_journey_progress` until the broader harvest/adopt
  workflow in `ISSUE.mentorhub_mentor_api.adopt_harvested_services.md` retires
  local services.

### Verify

- `pipenv run test`, `pipenv run lint`, `pipenv run build`
- `pipenv run container`, `pipenv run api`, `pipenv run e2e` — confirm no regressions
  from the library bump (Profile dashboard journey counts unchanged).

## Acceptance

- `Pipfile` pins `api-utils==0.5.2` (or current harvest patch).
- Full test and E2E suites green.
- No new imports of promote/detail methods unless explicitly scoped in a later task.
