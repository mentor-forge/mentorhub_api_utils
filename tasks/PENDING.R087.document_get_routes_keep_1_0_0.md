# R087 – Document shared GET routes; keep version 1.0.0

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R086_e2e_shared_get_routes`  
**Description**: README shows `create_*_get_routes(service_cls)` include pattern, simple `[...]` pagination, and demo-server GET prefixes. Version stays **`1.0.0`** (not tagged yet; this wave lands on the same PR). Point downstream ISSUE files at the factories.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — **Shared domain services**, **Standardized Get List pattern**, **Domain APIs vs. this library** (demo server paragraph)
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R080.bump_major_1_0_0.md` — already set `pyproject.toml` to `1.0.0`
- `tasks/SHIPPED.R084.shared_get_route_factories.md` / `PENDING.R084` if still named PENDING
- `pyproject.toml` — must remain `1.0.0`
- `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md`
- `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md`
- `tasks/ISSUE.mentorhub_customer_api.profile_control.md`
- `tasks/ISSUE.journey_api.md`

### Versioning

Do **not** bump to `1.1.0` or `1.0.1`. `1.0.0` is unpublished. R080 already made the major bump for F-UA12/13; GET route factories are additive on that same release.

### README must show

Include pattern (subclass + factory, routes still import local service):

```python
from api_utils.routes.shared_get_routes import create_resource_get_routes
from src.services.resource_service import ResourceService

def create_resource_routes():
    bp = create_resource_get_routes(ResourceService)
    @bp.route("", methods=["POST"])
    def create_resource():
        ...
    return bp
```

State clearly:

- List GET body is a JSON **array**; pagination is request headers `offset` / `size` only.
- Get-by-id returns the document or 404.
- No cursor envelope and no `X-Pagination-*` response headers in api_utils.
- Demo server (`api_utils/server.py`) mounts the same factories with shared `api_utils.services` classes for library e2e.
- Pin remains `api-utils==1.0.0`.

### ISSUE artifacts (append a short **Shared GET routes** note, do not rewrite harvest-back)

Tell each API to replace duplicated GET handlers with `create_*_get_routes(LocalService)` and add control POST/PATCH on the returned blueprint:

- Mentee: resource, path, note (list), event (list), journey (by-id only — keep local `GET ""` get-or-create), aggregation
- Mentor: resource, path, plan, profile, mentee, encounter, event
- Customer: profile list/get
- Journey ISSUE: by-id consume GET may come from the factory; `GET ""` stays Mentee-local

## Goals

- `pyproject.toml` version is still `1.0.0`.
- README documents factories, pagination, demo prefixes.
- ISSUE files mention adopting the factories.
- Import smoke: `pipenv run python -c "from api_utils import create_resource_get_routes, create_path_get_routes"`

## Testing Expectations

- `pipenv run test`
- `pipenv run lint` — R087 files `black`-clean
- `pipenv run build` — artifact still `api_utils-1.0.0-...`
- Import smoke as in Goals

## Outputs

- `README.md`
- `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md`
- `tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md`
- `tasks/ISSUE.mentorhub_customer_api.profile_control.md`
- `tasks/ISSUE.journey_api.md`
- `pyproject.toml` — only if a prior task accidentally bumped off `1.0.0` (restore it); otherwise do not touch

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
