# Discovery API: Notification control (dismiss) + consume GETs

> **Cross-repo issue artifact.** Paste-ready description for
> **`mentorhub_discovery_api`**. Not orchestrated from `mentorhub_api_utils`.
> **Blocked on**: `api-utils>=1.0.0` (R077 removes shared `dismiss_notification`;
> R082 outbound list/get).

## Summary

Discovery **controls** Notification; **creates** Event; **consumes** Profile,
Customer, Journey, Resource, Path, Plan (`architecture.yaml`). Shared
`NotificationService` keeps global `create_notification` and RBAC list.
Dismiss (and any cancel) belongs on the Discovery subclass.

## Pin

- `api-utils==1.0.0` via `pipenv run install`.

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

Harvested from `api_utils/services/notification_service.py` before R077.
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

## Other consume wrappers

Thin subclasses for Profile / Journey / Resource / Path / Plan GETs so routes
use `src.services`. Do **not** add control mutations for collections Discovery
does not control. Event POST uses inherited `EventService.create_event`.
Replace any remaining infinite-scroll Profile lists with shared offset/size GETs.

## Routes

- GET notifications → inherited `get_notifications` (outbound filter on shared)
- POST notification (if Discovery produces as well) → inherited `create_notification` plus inbound if you restrict who may broadcast
- PATCH/POST dismiss → local `dismiss_notification` (inbound + outbound-visible)
- Import local `NotificationService` only

## Acceptance

- Dismiss is not imported from `api_utils.services`.
- List still newest-first; dismiss writes only `dismissed`.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
