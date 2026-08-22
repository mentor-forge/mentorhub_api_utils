# Customer API: Profile control subclass (create + PATCH)

> **Cross-repo issue artifact.** Paste-ready description for
> **`mentorhub_customer_api`**. Not orchestrated from `mentorhub_api_utils`.
> **Blocked on**: `api-utils>=1.0.0` (R076 shared `create_profile` + R082 outbound GETs).

## Summary

Customer **controls** Customer, Payment, and Profile; **creates** Event
(`architecture.yaml`). Shared `ProfileService` provides GET (RBAC list/filter)
and **global** `create_profile`. This API's subclass adds Profile PATCH / mutate
(and any Customer-domain enrich). Routes import the local subclass.

## Pin

- `api-utils==1.0.0` via `pipenv run install`.

## `src/services/profile_service.py`

Replace the local infinite-scroll Profile service with:

```python
from api_utils.services import ProfileService as SharedProfileService

class ProfileService(SharedProfileService):
    @classmethod
    def update_profile(cls, profile_id, data, token, breadcrumb):
        # Customer control: restricted _id/created/saved; stamp saved; MongoIO.update_document
        ...
```

- Inherit `get_profile`, `get_profiles`, `get_profile_by_token`, `create_profile`.
- Drop `execute_infinite_scroll_query` / `after_id` (api_utils removed that module in R074).
- Use shared list filters/order if R076 exported `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER`.

## Routes

- Profile GET/list → local subclass (inherited shared GETs).
- Profile POST → `ProfileService.create_profile` (shared implementation via inherit).
- Profile PATCH → local `update_profile`.
- Event POST → inherit `EventService.create_event` (global POST).

Do not import `api_utils.services.ProfileService` in routes.

## Inbound RBAC (F-UA12)

Outbound list/get-by-id is on the shared class (own profile, same `customer_id`,
admin root, hide archived). This subclass adds **inbound** writes:

- `create_profile`: `ROLE_CUSTOMER` or `ROLE_ADMIN`; stamp `customer_id` from the token when the caller is a customer.
- `update_profile`: `ROLE_CUSTOMER` or admin; target Profile must be in the caller’s customer (or be the caller’s own profile). 403 if not.
- Do not 403 on GET here.

## Shared GET routes

Replace Profile GET/list handlers with
`create_profile_get_routes(ProfileService)` from `api_utils` (see
`tasks/SHIPPED.R084.shared_get_route_factories.md`). Add Profile POST/PATCH on
the returned blueprint. List GET body is a JSON array; pagination is
`offset`/`size` request headers only (no cursor, no `X-Pagination-*`).

## Acceptance

- Local `ProfileService` subclasses shared.
- Customer can create and patch Profile; list uses offset/size + RBAC match.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
