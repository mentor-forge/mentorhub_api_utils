# Adopt api-utils Journey promote + GET detail harvest; remove local services

> **Cross-repo issue artifact.** Paste-ready description for follow-on planning
> in **`mentorhub_mentee_api`**. Not part of the current `PENDING.*`
> orchestration chain in `mentorhub_api_utils` and must not be executed from
> that folder.
> **Blocked on**: `mentorhub_api_utils` R059–R061 shipped and published to
> CodeArtifact (`api-utils>=0.5.2`).

## Summary

Once `api_utils.services.journey_service.JourneyService` carries promote mutations
and GET profile enrichment (harvested from this repo's temporary local services),
the Mentee API should bump its `api-utils` pin, switch routes to the shared
class, and delete the local wrappers.

## Scope

### Dependency bump

- Pin `api-utils` to **`0.5.2`** (or the patch release that includes R059–R061)
  in `Pipfile` / `Pipfile.lock`.
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed).

### Switch routes (`src/routes/journey_routes.py`)

| Endpoint | Before | After |
|----------|--------|-------|
| `GET /api/journey` | `JourneyDetailService.get_my_journey_detail` | `JourneyService.get_my_journey_detail` |
| `PATCH .../promote/path/<path_id>` | `JourneyPromoteService.promote_path_to_next` | `JourneyService.promote_path_to_next` |
| `PATCH .../promote/module/<path_id>/<module_name>` | `JourneyPromoteService.promote_module_to_next` | `JourneyService.promote_module_to_next` |
| `PATCH .../advance/...`, `PATCH .../complete/...`, `PATCH /<id>` | `JourneyService.*` | unchanged |

- Remove imports of `JourneyDetailService` and `JourneyPromoteService`.
- Remove route-level PATCH guard `if "profile" in data: raise HTTPForbidden(...)` —
  `JourneyService.update_journey` now rejects `profile` via `RESTRICTED_UPDATE_FIELDS`.

### Remove local copies

- Delete `src/services/journey_promote_service.py`
- Delete `src/services/journey_detail_service.py`
- Delete `src/services/__init__.py` if the directory becomes empty
- Delete `test/services/test_journey_promote_service.py`
- Delete `test/services/test_journey_detail_service.py`
- Update `test/routes/test_journey_routes.py` patch targets to `JourneyService.*`

### Contract verification (no behavior drift)

- **GET** `/api/journey` returns **`JourneyDetail`** shape (Journey fields + embedded `profile`).
- **PATCH promote/advance/complete** and **PATCH `/<id>`** return plain **`Journey`** without `profile`.
- OpenAPI (`docs/openapi.yaml`) unchanged except if version pin is documented in README.

## Acceptance

- Routes call `api_utils.services.JourneyService` only for journey domain logic.
- Confirmation (`rg 'JourneyPromoteService\|JourneyDetailService\|src\.services\.journey'`) that no local journey service imports remain.
- `pipenv run test`, `pipenv run lint`, `pipenv run build` pass.
- `pipenv run container`, `pipenv run api`, `pipenv run e2e` pass (promote and GET detail scenarios from L193–L199 / F197–F199).

## Supersedes

- `tasks/ISSUE.mentorhub_api_utils.adopt_journey_promote_from_api_utils.md` — promote-only adopt; fold into this issue after full harvest ships.
