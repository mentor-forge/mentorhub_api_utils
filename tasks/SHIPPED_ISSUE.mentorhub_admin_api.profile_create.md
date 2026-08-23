Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_admin_api/issues/5

# F-AA03: Pin api-utils 1.0.0 and add Admin Profile create + ExternalEvent ingress

This is the **first** `mentorhub_admin_api` issue for the 1.0.0 wave. It owns
the `api-utils==1.0.0` pin bump.

## Summary

Admin **controls** ExternalEvent and Setting; **creates** Event and Profile;
**consumes** Profile and Customer (`architecture.yaml`). Today this repo pins
`api-utils==0.5.2` and is a stub: `src/server.py` registers only config,
metrics, and explorer — there is no `src/services/` and no domain routes.

Pin **1.0.0**, then add thin local subclasses so routes never import shared
service classes directly.

## Pin (this issue owns the bump)

- Set `api-utils==1.0.0` in `Pipfile` / `Pipfile.lock` (currently `==0.5.2`).
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed). Do **not**
  use bare `pipenv install`.

## Services

```python
from api_utils.services import ProfileService as SharedProfileService
from api_utils.services import ExternalEventService as SharedExternalEventService
from api_utils.services import EventService as SharedEventService

class ProfileService(SharedProfileService):
    """Admin may create Profile (shared create_profile). No Profile PATCH here —
    Customer controls Profile."""

class ExternalEventService(SharedExternalEventService):
    """Ingress POST; add Admin-only RBAC on create if required."""

class EventService(SharedEventService):
    pass
```

Override `_check_permission` on the Admin Profile subclass so **inbound**
`create_profile` requires `ROLE_ADMIN` (admin is root for other collections too).
Shared create has no write check — this subclass supplies it. Customer API has
its own inbound create check. Do not PATCH Profile here (Customer **controls**
Profile). ExternalEvent create: `ROLE_ADMIN`. Event create: any authenticated
or admin-only if this API is operators-only — prefer `ROLE_ADMIN` for ingress.

Shared `ExternalEventService` already has `create_external_event` (append-only)
and `get_external_event`. Outbound GET for ExternalEvent is admin-only
(`EMPTY_SCOPE_MATCH` for non-admin).

## Routes

- POST Profile → `src.services.profile_service.ProfileService.create_profile`
- POST ExternalEvent → local subclass `create_external_event`
- GET Profile (consume) → `create_profile_get_routes(ProfileService)`
- GET ExternalEvent → `create_external_event_get_routes(ExternalEventService)`
- Event POST/list → `create_event_get_routes(EventService)` plus POST create

Register the new blueprints from `src/server.py` (today only config/metrics/explorer).

## Shared GET routes

Use factories from `api_utils.routes.shared_get_routes`. Add control POST on
the returned blueprint. List GET body is a JSON array; pagination is
`offset`/`size` request headers only (no cursor, no `X-Pagination-*`).

| Route module | Factory | Notes |
|--------------|---------|-------|
| `profile_routes.py` | `create_profile_get_routes(ProfileService)` | add POST create |
| `external_event_routes.py` | `create_external_event_get_routes(ExternalEventService)` | by-id only; add POST create |
| `event_routes.py` | `create_event_get_routes(EventService)` | list; add POST create |

## Acceptance

- `Pipfile` pins `api-utils==1.0.0`.
- Routes import local subclasses.
- Admin can create Profile and ExternalEvent; Admin does not PATCH Profile.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
