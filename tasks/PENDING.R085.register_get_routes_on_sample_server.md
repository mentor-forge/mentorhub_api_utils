# R085 – Register shared GET routes on the demo server

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R084_shared_get_route_factories`  
**Description**: Mount every `create_*_get_routes` factory on the api_utils demo server using the **shared** service classes (this process has no domain subclass). Update demo OpenAPI paths.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md` — route registration grouped in `server.py`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R084.shared_get_route_factories.md` (treat as SHIPPED if already renamed) — factory names and URL shapes
- `api_utils/server.py`
- `docs/openapi.yaml` — currently documents `/api/config` and `/metrics` only
- `api_utils/routes/shared_get_routes.py`

The demo server is the library test harness, not a journey domain. Passing `ResourceService` (etc.) from `api_utils.services` here is correct. Domain APIs still pass their subclass.

### Prefixes

| Blueprint factory | `url_prefix` |
|-------------------|--------------|
| `create_resource_get_routes` | `/api/resource` |
| `create_path_get_routes` | `/api/path` |
| `create_plan_get_routes` | `/api/plan` |
| `create_profile_get_routes` | `/api/profile` |
| `create_notification_get_routes` | `/api/notification` |
| `create_event_get_routes` | `/api/event` |
| `create_note_get_routes` | `/api/note` |
| `create_journey_get_routes` | `/api/journey` |
| `create_encounter_get_routes` | `/api/encounter` |
| `create_mentee_get_routes` | `/api/mentee` |
| `create_aggregation_get_routes` | `/api/aggregation` |
| `create_external_event_get_routes` | `/api/external-event` |

Log the new prefixes next to the existing `/docs`, `/api/config`, `/metrics` lines.

OpenAPI: add GET operations for each mounted path (list vs id). Document `offset`/`size` **headers**, query filters/sort where the factory uses `parse_list_request`, Bearer auth, `200` array or document, `401`, `404`. Do not invent full MongoDB dictionary component schemas — a generic object/array is enough for the demo spec.

## Goals

- `api_utils/server.py` registers all twelve GET blueprints.
- Demo OpenAPI lists those GETs with the simple pagination contract.
- Existing config/metrics e2e still apply (no behavior change to those routes).
- No version bump.

## Testing Expectations

- `pipenv run test`
- `PYTHONPATH=. pipenv run pytest tests/test_server.py` — existing e2e still collected (may skip if server down; unit collection must succeed)
- `pipenv run lint` — R085 files `black`-clean
- `pipenv run build`

Full black-box GET coverage is R086 (`pipenv run e2e` against `pipenv run dev`).

## Outputs

- `api_utils/server.py`
- `docs/openapi.yaml`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
