Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_discovery_api/issues/6

# F-DA03: Discovery API Notification control (dismiss) + consume GETs

Follows **F-DA02** (pin `api-utils==1.0.0` and list migration). Do not re-bump
the pin.

## Summary

Discovery **controls** Notification; **creates** Event; **consumes** Profile,
Customer, Journey, Resource, Path, Plan (`architecture.yaml`). Shared
`NotificationService` keeps global `create_notification` and RBAC list
(`get_notifications`, newest-first). Dismiss (and any cancel) belongs on the
Discovery subclass.

Today this repo only has local Customer and Profile services (no Notification
routes yet). Add `src/services/notification_service.py` and GET/dismiss routes.

## Pin

- Already `api-utils==1.0.0` from F-DA02. `pipenv run install` if needed.

## `src/services/notification_service.py`

```python
from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import HTTPForbidden, HTTPNotFound, HTTPInternalServerError
from api_utils.services import NotificationService as SharedNotificationService

class NotificationService(SharedNotificationService):
    @classmethod
    def dismiss_notification(cls, notification_id, token, breadcrumb):
        try:
            cls._check_permission(token, "update")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            updated = mongo.update_document(
                config.NOTIFICATION_COLLECTION_NAME,
                document_id=notification_id,
                set_data={"dismissed": breadcrumb},
            )
            if updated is None:
                raise HTTPNotFound(f"Notification {notification_id} not found")
            return updated
        except (HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            raise HTTPInternalServerError(
                f"Failed to dismiss notification {notification_id}"
            )
```

Harvested from `api_utils/services/notification_service.py` before R077
(`git show 9af2886:api_utils/services/notification_service.py`).
There is **no** `saved` field on Notification. `dismissed` is a breadcrumb,
not a boolean.

Optional: `cancel_notification` setting `cancelled` breadcrumb (same shape).

Before dismiss, load the notification with the **shared** get (outbound
post-fetch). If the caller cannot see it, they get 404. Then set `dismissed`.
Inbound: authenticated user whose token matches the notification’s target
(`profile_id` / `customer_id` / `mentor_id`) or admin — same population as
outbound; 403 only if a visible notification is dismissed by someone who
should not mutate (rare if outbound already scoped). Prefer: load via parent
GET, then write.

Shared list is `get_notifications` (not a by-id get). Load via
`execute_list_query` / `MongoIO.get_document` then `require_outbound` /
`matches_outbound` from `api_utils.services.rbac` if you need a single-doc
read before dismiss.

## Other consume wrappers

Thin subclasses for Profile / Journey / Resource / Path / Plan GETs so routes
use `src.services`. Do **not** add control mutations for collections Discovery
does not control. Event POST uses inherited `EventService.create_event`.
Profile lists should already be shared offset/size GETs from F-DA02.

## Routes

- GET notifications → `create_notification_get_routes(NotificationService)`
  (inherited `get_notifications`, outbound filter on shared)
- POST notification (if Discovery produces as well) → inherited
  `create_notification` plus inbound if you restrict who may broadcast
- PATCH/POST dismiss → local `dismiss_notification` (inbound + outbound-visible)
- Import local `NotificationService` only

## Shared GET routes

Replace duplicated GET handlers with factories from
`api_utils.routes.shared_get_routes`. List GET body is a JSON array;
pagination is `offset`/`size` request headers only (no cursor, no
`X-Pagination-*`).

| Route module | Factory | Notes |
|--------------|---------|-------|
| `notification_routes.py` | `create_notification_get_routes(NotificationService)` | list only; add dismiss PATCH |
| `profile_routes.py` | `create_profile_get_routes(ProfileService)` | from F-DA02 |
| `journey_routes.py` | `create_journey_get_routes(JourneyService)` | by-id only |
| `resource_routes.py` | `create_resource_get_routes(ResourceService)` | consume |
| `path_routes.py` | `create_path_get_routes(PathService)` | consume |
| `plan_routes.py` | `create_plan_get_routes(PlanService)` | consume |
| `event_routes.py` | `create_event_get_routes(EventService)` | list; add POST create |

## Acceptance

- Dismiss is not imported from `api_utils.services`.
- List still newest-first; dismiss writes only `dismissed`.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
