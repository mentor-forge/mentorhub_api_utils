# Adopt api-utils Journey harvest (interim bump; progress still local)

> **Cross-repo issue artifact.** Paste-ready description for follow-on planning
> in **`mentorhub_mentor_api`**. Not part of the current `PENDING.*`
> orchestration chain in `mentorhub_api_utils` and must not be executed from
> that folder.
> **Blocked on**: `mentorhub_api_utils` R059–R061 shipped and published to
> CodeArtifact (`api-utils>=0.5.2`).

## Summary

**R059–R061 did not harvest `get_journey_progress`.** Those tasks moved only the
mentee-API Journey surface (promote mutations + GET profile enrichment) into
`api_utils.services.journey_service`. The Mentor API's local
`src/services/journey_service.py` — which exposes **`get_journey_progress`** for
the Profile dashboard — **remains required** after pinning `0.5.2`.

Bumping to `0.5.2` keeps this repo on the current library release but **does
not** allow deleting `src/services/`. Full retirement of local services
(including Journey progress) is blocked on
**`ISSUE.mentorhub_api_utils.harvest_mentor_services.md`**, which explicitly
lists adding `get_journey_progress` to upstream `JourneyService`, followed by
**`ISSUE.mentorhub_mentor_api.adopt_harvested_services.md`**.

## What `api-utils==0.5.2` adds (Journey)

| Method | In 0.5.2? | Used by Mentor API today? |
|--------|-----------|---------------------------|
| `promote_path_to_next` / `promote_module_to_next` | Yes | No |
| `get_my_journey_detail` | Yes | No |
| `get_journey_progress` | **No** | **Yes** — `ProfileService` dashboard/detail |

## Scope for this issue (interim)

### Dependency bump

- Pin `api-utils` to **`0.5.2`** in `Pipfile` / `Pipfile.lock`.
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed).

### What to change

- **Bump only** — no route or service refactors in this issue.

### What NOT to do yet

- Do **not** delete `src/services/journey_service.py` — `ProfileService` still
  imports `JourneyService.get_journey_progress` from the local module.
- Do **not** expect routes to call `api_utils.services.JourneyService` for
  dashboard progress; that method does not exist upstream until
  `harvest_mentor_services` ships.
- Do **not** conflate this issue with
  **`ISSUE.mentorhub_mentor_api.adopt_harvested_services.md`** (full
  `src/services/` deletion).

### Verify

- `pipenv run test`, `pipenv run lint`, `pipenv run build`
- `pipenv run container`, `pipenv run api`, `pipenv run e2e` — Profile dashboard
  journey counts unchanged.

## Acceptance

- `Pipfile` pins `api-utils==0.5.2`.
- Local `src/services/journey_service.py` **still present** (progress aggregation).
- Full test and E2E suites green.

## Path to delete all local services

1. **`mentorhub_api_utils`** — execute `ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
   (includes `get_journey_progress` on shared `JourneyService` + Plan/Encounter/Mentee/Profile).
2. Publish new `api-utils` minor (e.g. `0.6.0`) via `tag-release`.
3. **`mentorhub_mentor_api`** — execute `ISSUE.mentorhub_mentor_api.adopt_harvested_services.md`:
   routes call `api_utils.services.*` directly; delete entire `src/services/`.
