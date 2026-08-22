# Admin API: Profile create + ExternalEvent ingress

> **Cross-repo issue artifact.** Paste-ready description for
> **`mentorhub_admin_api`**. Not orchestrated from `mentorhub_api_utils`.
> **Blocked on**: `api-utils>=1.0.0` (R076 shared `create_profile`; ExternalEvent
> create stays shared as append-only; R082 outbound GETs).

## Summary

Admin **controls** ExternalEvent and Setting; **creates** Event and Profile;
**consumes** Profile and Customer (`architecture.yaml`). Add thin local
subclasses so routes never import shared service classes directly.

## Pin

- `api-utils==1.0.0` via `pipenv run install`.

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

## Routes

- POST Profile → `src.services.profile_service.ProfileService.create_profile`
- POST ExternalEvent → local subclass
- GET Profile (consume) → inherited `get_profile` / `get_profiles`

## Acceptance

- Routes import local subclasses.
- Admin can create Profile and ExternalEvent; Admin does not PATCH Profile.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
