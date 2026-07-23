# Bump api-utils to 0.6.0 and adopt harvested services (retire local `src/services/`)

> **Cross-repo issue artifact.** Paste-ready description for follow-on planning
> in **`mentorhub_mentor_api`**. Not part of this repo's `PENDING.*`
> orchestration chain and must not be executed from `mentorhub_api_utils/tasks/`.
> **Blocked on**: `mentorhub_api_utils` R062–R066 shipped and published to
> CodeArtifact (`api-utils>=0.6.0`).

## Summary

`mentorhub_api_utils` `0.6.0` completes the shared service surface: the Mentor
API's remaining local services — `PlanService`, `MenteeService`,
`EncounterService`, `ProfileService` — are now harvested into
`api_utils.services`, and `JourneyService.get_journey_progress` (the mentor
dashboard aggregation that R059–R061 did **not** harvest) is finally upstream.

With `0.6.0` pinned, `mentorhub_mentor_api` can point its routes directly at
`api_utils.services.*` and **delete the entire `src/services/` package**. This
issue supersedes the interim
`ISSUE.mentorhub_mentor_api.bump_api_utils_journey_harvest.md`, which explicitly
kept `src/services/journey_service.py` alive only because `get_journey_progress`
was still local.

## What `api-utils==0.6.0` adds

| Shared service | Methods now upstream |
|----------------|----------------------|
| `JourneyService` | `get_journey_progress` (library/now/next counts) — the last local Journey method |
| `PlanService` | `create_plan`, `get_plans`, `get_plan`, `update_plan` |
| `MenteeService` | `get_mentee` (create-if-missing), `update_mentee` |
| `EncounterService` | `create_encounter` (agenda autofill from Plan), `get_encounter`, `update_encounter` (owner-or-admin), `get_recent_encounter`, `get_encounters_for_mentee` |
| `ProfileService` | `get_profile_by_token`, `get_profiles` (dashboard), `get_profile` (detail), `get_profile_properties` |

## Scope for this issue

### Dependency bump

- Pin `api-utils` to **`0.6.0`** in `Pipfile` / `Pipfile.lock`.
- Install via the CodeArtifact wrapper: `pipenv run install` (run `mh` first if
  credentials are not already available). Do **not** use bare `pipenv install`.

### Route adoption

- Update route/controller imports from `from src.services.<x> import <Y>` to
  `from api_utils.services import <Y>` for Plan, Mentee, Encounter, Profile, and
  the Journey progress calls.
- Verify method signatures are unchanged (they were harvested behavior-for-behavior);
  no route logic changes expected beyond the import source.

### Delete local services

- Remove the entire `src/services/` package (`plan_service.py`,
  `mentee_service.py`, `encounter_service.py`, `profile_service.py`,
  `journey_service.py`, `event_service.py`, `path_service.py`,
  `resource_service.py`, and `__init__.py`) once no route or test imports
  `src.services.*`.
- Move/rewrite any service-level unit tests that should live upstream; keep only
  route/integration tests locally and repoint their patch targets to
  `api_utils.services.*`.

### What NOT to do

- Do not re-implement or fork any harvested behavior locally.
- Do not change the OpenAPI contract or route paths in this issue.

## Verify

- `pipenv run install`
- `pipenv run test`, `pipenv run lint`, `pipenv run build`
- `pipenv run container`, `pipenv run api`, `pipenv run e2e` — Mentor Dashboard
  (profiles + journey progress + recent encounter), Profile detail, Plan CRUD,
  Encounter create/patch, and Mentee notes all behave unchanged.

## Acceptance

- `Pipfile` pins `api-utils==0.6.0`.
- `src/services/` no longer exists; routes import `api_utils.services.*`.
- Full unit + E2E suites green.
- Interim `ISSUE.mentorhub_mentor_api.bump_api_utils_journey_harvest.md` is
  closed/superseded by this adoption.
