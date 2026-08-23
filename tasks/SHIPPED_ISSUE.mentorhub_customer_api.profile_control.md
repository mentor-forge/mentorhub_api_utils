Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_customer_api/issues/17

# F-CA15: Customer API Profile control subclass (create + PATCH)

Follows **F-CA14** (pin `api-utils==1.0.0` and list migration). Do not re-bump
the pin.

## Summary

Customer **controls** Customer, Payment, and Profile; **creates** Event
(`architecture.yaml`). Shared `ProfileService` provides GET (RBAC list/filter)
and **global** `create_profile`. This API's subclass adds Profile PATCH / mutate
(and any Customer-domain enrich). Routes import the local subclass.

F-CA14 should already have a thin `ProfileService(SharedProfileService)` and
`create_profile_get_routes`. This issue adds inbound write checks and PATCH.

## Pin

- Already `api-utils==1.0.0` from F-CA14. `pipenv run install` if the lockfile
  needs a refresh.

## `src/services/profile_service.py`

```python
from api_utils.services import ProfileService as SharedProfileService

class ProfileService(SharedProfileService):
    @classmethod
    def update_profile(cls, profile_id, data, token, breadcrumb):
        # Customer control: restricted _id/created/saved; stamp saved; MongoIO.update_document
        ...
```

- Inherit `get_profile`, `get_profiles`, `get_profile_by_token`, `create_profile`.
- Shared list filters/order: `PROFILE_LIST_FILTERS` / `PROFILE_LIST_ORDER` on
  `api_utils.services.profile_service`.
- No `execute_infinite_scroll_query` / `after_id` (removed from api_utils in R074).

## Routes

- Profile GET/list → `create_profile_get_routes(ProfileService)` (from F-CA14).
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

Keep `create_profile_get_routes(ProfileService)` from
`api_utils.routes.shared_get_routes`. Add Profile POST/PATCH on the returned
blueprint. List GET body is a JSON array; pagination is `offset`/`size`
request headers only (no cursor, no `X-Pagination-*`).

## Acceptance

- Local `ProfileService` subclasses shared.
- Customer can create and patch Profile; list uses offset/size + RBAC match.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
