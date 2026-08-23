Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_mentee_api/issues/26

# F-EA12: Pin api-utils 1.0.0 and restore Journey control on a Mentee subclass

This is the **first** `mentorhub_mentee_api` issue for the 1.0.0 wave. It owns
the `api-utils==1.0.0` pin bump. Ship in the **same PR** as
`SHIPPED_ISSUE.mentorhub_mentee_api.extend_shared_services.md` — 1.0.0 strips Journey
mutations **and** Note/Aggregation/Path enrich that those routes still call.

`architecture.yaml`: Mentee **controls** Journey; Customer and Discovery
**consume** it. Shared `api_utils.services.JourneyService` keeps GET-by-id
(`get_journey`, outbound 404 when hidden) and `get_journey_progress` only.
This file holds the post / patch / mutate (and get-or-create / enrich) code
removed from the shared class in R078.

## Summary

Today this repo pins `api-utils==0.5.2` and has **no** `src/services/` —
routes import `api_utils.services.JourneyService` directly and still call
`get_my_journey_detail`, promote, advance, complete, and `update_journey`.
Those methods are gone in **1.0.0**.

Pin `api-utils==1.0.0`. Recreate `src/services/journey_service.py` as a
**subclass** of `api_utils.services.JourneyService`. Put clone-on-GET, profile
enrich, create, PATCH, promote, advance, and complete on the subclass.
Point `src/routes/journey_routes.py` at the **local** class.

`complete_resource` calls local `AggregationService.add_completion` from the
paired extend-shared-services issue.

## Pin (this issue owns the bump)

- Set `api-utils==1.0.0` in `Pipfile` / `Pipfile.lock`.
- Install with `pipenv run install` (CodeArtifact auth; run `mh` first if
  needed). Do **not** use bare `pipenv install`.

## Pattern

```python
# src/services/journey_service.py
from api_utils.services import JourneyService as SharedJourneyService
from api_utils.services.journey_service import TEMPLATE_JOURNEY_ID

class JourneyService(SharedJourneyService):
    ...

# src/routes/journey_routes.py
from src.services.journey_service import JourneyService
```

Do **not** import `JourneyService` from `api_utils.services` in routes.

## Inbound RBAC (F-UA12)

Outbound visibility is already applied in shared GETs (`api-utils>=1.0.0`). This subclass owns **inbound** who-may-write:

- `update` / `mutate` / `complete` / template clone: existing `_check_permission` in the harvest-back source below.
- Do **not** 403 on GET in this subclass — hide via outbound 404 from the parent.
- Admin remains root on inbound as well (`ROLE_ADMIN` already bypasses update in the harvest-back).

## Shared GET routes

By-id consume GET may come from
`create_journey_get_routes(JourneyService)` (returns `/<journey_id>` only; no
list). **`GET /api/journey` (`""`) stays Mentee-local** for get-or-create /
`get_my_journey_detail`. Add control PATCH routes on the same blueprint. See `api_utils.routes.shared_get_routes.create_journey_get_routes`.

## Route mapping (unchanged HTTP contract)

| Endpoint | Local method |
|----------|----------------|
| `GET /api/journey` | `JourneyService.get_my_journey_detail` |
| `PATCH /api/journey/promote/path/<path_id>` | `promote_path_to_next` |
| `PATCH /api/journey/promote/module/<path_id>/<module_name>` | `promote_module_to_next` |
| `PATCH /api/journey/advance/<resource_id>` | `advance_resource` |
| `PATCH /api/journey/complete/<resource_id>` | `complete_resource` |
| `PATCH /api/journey/<journey_id>` | `update_journey` |

Shared parent still provides `get_journey(journey_id, token, breadcrumb)`
(404 if missing) and `get_journey_progress`. `get_my_journey` is **not** on
the parent — it is get-or-create and lives here.

## Shared vs local

| On `api_utils.services.JourneyService` | On Mentee subclass |
|----------------------------------------|--------------------|
| `get_journey`, `get_journey_progress` | `_clone_template`, `get_my_journey`, `get_my_journey_detail` |
| `_oid`, `_validate_object_id` | `create_journey`, `update_journey` |
| `TEMPLATE_JOURNEY_ID` (import) | `advance_resource`, `complete_resource`, promote* |
| read `_check_permission` | write `_check_permission` (update / mutate / complete) |

## Tests to port from api_utils

Copy behavior from git history of `mentorhub_api_utils` at **`9af2886`**
(classmethod form, before R078 strip):

- `tests/services/test_journey_service.py` — get_my_journey clone, update RBAC, advance, complete, promote, get_my_journey_detail
- `tests/services/test_journey_service_integration.py` — clone validity, advance/complete round trip, promote

Keep route tests; patch `src.routes.journey_routes.JourneyService.*`.

## Acceptance

- `Pipfile` pins `api-utils==1.0.0`.
- `src/services/journey_service.py` exists and subclasses the shared class.
- Routes import `from src.services.journey_service import JourneyService`.
- GET still returns Journey + embedded `profile`; PATCH mutations return plain Journey.
- Lands in the same PR as the extend-shared-services issue.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`, `pipenv run e2e` pass.

---

## Harvest-back source (classmethod form)

Paste into `src/services/journey_service.py`. Converted from
`api_utils/services/journey_service.py` before R078 (classmethod form). Parent
`get_journey` raises `HTTPNotFound` when missing or hidden by outbound RBAC —
`get_my_journey` clones in that case.
MongoDB I/O stays on **MongoIO**. `complete_resource` uses local
`AggregationService.add_completion` (Mentee subclass) and shared
`EventService.create_event`.

```python
"""Mentee Journey control: clone-on-GET, enrich, PATCH, promote/advance/complete."""

import copy
import logging

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.services import JourneyService as SharedJourneyService
from api_utils.services.journey_service import TEMPLATE_JOURNEY_ID

logger = logging.getLogger(__name__)

RESTRICTED_UPDATE_FIELDS = [
    "_id",
    "profile_id",
    "created",
    "saved",
    "library",
    "now",
    "next",
    "profile",
]


class JourneyService(SharedJourneyService):
    """Mentee-domain Journey writes and BFF enrich."""

    @classmethod
    def _check_permission(cls, token, operation, journey_id=None):
        if operation == "read":
            return super()._check_permission(token, operation)
        if operation == "update":
            profile_id = token.get("profile_id")
            roles = token.get("roles", [])
            if journey_id == profile_id or "admin" in roles:
                return
            raise HTTPForbidden("Insufficient permissions to update this journey")
        if operation == "mutate":
            if token.get("profile_id"):
                return
            raise HTTPForbidden("Insufficient permissions for this journey operation")
        if operation == "complete":
            roles = token.get("roles", [])
            if Config.get_instance().ROLE_MENTEE in roles:
                return
            raise HTTPForbidden("Mentee role required to complete resources")
        if operation == "create":
            return

    @classmethod
    def _validate_update_data(cls, data):
        for field in RESTRICTED_UPDATE_FIELDS:
            if field in data:
                raise HTTPForbidden(f"Cannot update {field} field")

    @classmethod
    def _clone_template(cls, profile_id, breadcrumb):
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        template = mongo.get_document(
            config.JOURNEY_COLLECTION_NAME, TEMPLATE_JOURNEY_ID
        )
        if template is None:
            raise HTTPNotFound(f"Template journey {TEMPLATE_JOURNEY_ID} not found")

        document = {
            "_id": profile_id,
            "profile_id": profile_id,
            "status": template.get("status", "active"),
            "library": copy.deepcopy(template.get("library", [])),
            "now": copy.deepcopy(template.get("now", [])),
            "next": copy.deepcopy(template.get("next", [])),
            "later": copy.deepcopy(template.get("later", [])),
            "created": breadcrumb,
            "saved": breadcrumb,
        }
        encode_document(document, ["_id", "profile_id"], [])
        mongo.create_document(config.JOURNEY_COLLECTION_NAME, document)
        created = mongo.get_document(config.JOURNEY_COLLECTION_NAME, profile_id)
        logger.info(f"Created journey {profile_id} from template for user {profile_id}")
        return created

    @classmethod
    def get_my_journey(cls, token, breadcrumb):
        try:
            cls._check_permission(token, "read")
            profile_id = token.get("profile_id")
            if not profile_id:
                raise HTTPBadRequest("profile_id is required on token")
            try:
                journey = cls.get_journey(profile_id, token, breadcrumb)
                logger.info(
                    f"Retrieved journey {profile_id} for user {token.get('user_id')}"
                )
                return journey
            except HTTPNotFound:
                return cls._clone_template(profile_id, breadcrumb)
        except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error retrieving journey for profile {profile_id}: {e}")
            raise HTTPInternalServerError("Failed to retrieve journey")

    @classmethod
    def get_my_journey_detail(cls, token, breadcrumb):
        try:
            profile_id = token.get("profile_id")
            if not profile_id:
                raise HTTPBadRequest("profile_id is required on token")

            journey = cls.get_my_journey(token, breadcrumb)

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            profile = mongo.get_document(config.PROFILE_COLLECTION_NAME, profile_id)
            if profile is None:
                raise HTTPNotFound(f"Profile {profile_id} not found")

            logger.info(
                f"Retrieved journey detail with profile {profile_id} "
                f"for user {token.get('user_id')}"
            )
            return {**journey, "profile": profile}
        except (HTTPBadRequest, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving journey detail for profile {token.get('profile_id')}: {e}"
            )
            raise HTTPInternalServerError("Failed to retrieve journey detail")

    @classmethod
    def create_journey(cls, data, token, breadcrumb):
        try:
            cls._check_permission(token, "create")
            if "_id" in data:
                del data["_id"]
            data["created"] = breadcrumb
            data["saved"] = breadcrumb

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            journey_id = mongo.create_document(config.JOURNEY_COLLECTION_NAME, data)
            logger.info(f"Created journey {journey_id} for user {token.get('user_id')}")
            return journey_id
        except HTTPForbidden:
            raise
        except Exception as e:
            logger.error(f"Error creating journey: {e}")
            raise HTTPInternalServerError(f"Failed to create journey: {e}")

    @classmethod
    def update_journey(cls, journey_id, data, token, breadcrumb):
        try:
            cls._check_permission(token, "update", journey_id=journey_id)
            cls._validate_update_data(data)

            set_data = {
                k: v for k, v in data.items() if k not in RESTRICTED_UPDATE_FIELDS
            }
            set_data["saved"] = breadcrumb

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            updated = mongo.update_document(
                config.JOURNEY_COLLECTION_NAME,
                document_id=journey_id,
                set_data=set_data,
            )
            if updated is None:
                raise HTTPNotFound(f"Journey {journey_id} not found")

            logger.info(f"Updated journey {journey_id} for user {token.get('user_id')}")
            return updated
        except (HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error updating journey {journey_id}: {e}")
            raise HTTPInternalServerError(f"Failed to update journey {journey_id}")

    @classmethod
    def _resource_id_in_next(cls, next_modules, resource_id):
        target = cls._oid(resource_id)
        for module in next_modules:
            for topic in module.get("topics", []):
                for rid in topic.get("resources", []):
                    if cls._oid(rid) == target:
                        return True
        return False

    @classmethod
    def _remove_resource_from_next(cls, next_modules, resource_id):
        target = cls._oid(resource_id)
        found = False
        new_modules = []
        for module in next_modules:
            new_topics = []
            for topic in module.get("topics", []):
                resources = topic.get("resources", [])
                kept = [r for r in resources if cls._oid(r) != target]
                if len(kept) != len(resources):
                    found = True
                if kept:
                    topic_copy = copy.deepcopy(topic)
                    topic_copy["resources"] = kept
                    new_topics.append(topic_copy)
            if new_topics:
                module_copy = copy.deepcopy(module)
                module_copy["topics"] = new_topics
                new_modules.append(module_copy)
        return found, new_modules

    @classmethod
    def _find_now_entry(cls, now_items, resource):
        resource_oid = cls._oid(resource["_id"])
        for index, item in enumerate(now_items):
            rid = item.get("resource_id")
            if rid is not None and cls._oid(rid) == resource_oid:
                return index, item
        return None, None

    @classmethod
    def _event_token(cls, token, resource_id, journey_id):
        event_token = dict(token)
        event_token["resource_id"] = resource_id
        event_token["journey_id"] = journey_id
        return event_token

    @classmethod
    def advance_resource(cls, resource_id, token, breadcrumb):
        try:
            cls._check_permission(token, "mutate")
            cls._validate_object_id(resource_id, "resource_id")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            resource = mongo.get_document(config.RESOURCE_COLLECTION_NAME, resource_id)
            if resource is None:
                raise HTTPNotFound(f"Resource {resource_id} not found")

            journey = cls.get_my_journey(token, breadcrumb)
            journey_id = str(journey["_id"])
            next_modules = journey.get("next", [])

            if not cls._resource_id_in_next(next_modules, resource_id):
                raise HTTPNotFound(
                    f"Resource {resource_id} not found in journey next scope"
                )

            found, updated_next = cls._remove_resource_from_next(
                next_modules, resource_id
            )
            if not found:
                raise HTTPNotFound(
                    f"Resource {resource_id} not found in journey next scope"
                )

            now_item = {
                "resource_id": resource_id,
                "added": breadcrumb["at_time"],
                "used": 0,
            }
            now_items = copy.deepcopy(journey.get("now", []))
            now_items.append(now_item)

            set_data = {
                "next": updated_next,
                "now": now_items,
                "saved": breadcrumb,
            }
            encode_document(
                set_data, ["resources", "resource_id"], ["added", "started"]
            )
            updated = mongo.update_document(
                config.JOURNEY_COLLECTION_NAME,
                document_id=journey_id,
                set_data=set_data,
            )

            from api_utils.services.event_service import EventService

            EventService.create_event(
                {"type": config.EVENT_TYPE_ADVANCED},
                cls._event_token(token, resource_id, journey_id),
                breadcrumb,
            )

            logger.info(f"Advanced resource {resource_id} for journey {journey_id}")
            return updated
        except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error advancing resource {resource_id}: {e}")
            raise HTTPInternalServerError(f"Failed to advance resource {resource_id}")

    @classmethod
    def complete_resource(cls, resource_id, data, token, breadcrumb):
        try:
            cls._check_permission(token, "complete")
            cls._validate_object_id(resource_id, "resource_id")
            data = data or {}

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            resource = mongo.get_document(config.RESOURCE_COLLECTION_NAME, resource_id)
            if resource is None:
                raise HTTPNotFound(f"Resource {resource_id} not found")

            journey = cls.get_my_journey(token, breadcrumb)
            journey_id = str(journey["_id"])
            now_items = copy.deepcopy(journey.get("now", []))

            index, now_entry = cls._find_now_entry(now_items, resource)
            if index is None:
                raise HTTPNotFound(
                    f"Resource {resource_id} not found in journey now scope"
                )

            now_items.pop(index)
            library_item = {
                "resource_id": resource_id,
                "started": now_entry.get("started") or breadcrumb["at_time"],
                "completed": breadcrumb["at_time"],
                "used": now_entry.get("used", 0),
            }
            rating = data.get("rating")
            if rating is not None:
                library_item["rating"] = rating

            library_items = copy.deepcopy(journey.get("library", []))
            library_items.append(library_item)

            set_data = {
                "now": now_items,
                "library": library_items,
                "saved": breadcrumb,
            }
            encode_document(
                set_data, ["resource_id"], ["added", "started", "completed"]
            )
            updated = mongo.update_document(
                config.JOURNEY_COLLECTION_NAME,
                document_id=journey_id,
                set_data=set_data,
            )

            from src.services.aggregation_service import AggregationService
            from api_utils.services.event_service import EventService

            AggregationService.add_completion(
                resource_id,
                rating,
                data.get("note"),
                data.get("duration"),
                token,
                breadcrumb,
            )
            EventService.create_event(
                {"type": config.EVENT_TYPE_COMPLETED},
                cls._event_token(token, resource_id, journey_id),
                breadcrumb,
            )

            logger.info(f"Completed resource {resource_id} for journey {journey_id}")
            return updated
        except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error completing resource {resource_id}: {e}")
            raise HTTPInternalServerError(f"Failed to complete resource {resource_id}")

    @classmethod
    def _path_id_in_later(cls, later_items, path_id):
        target = cls._oid(path_id)
        return any(cls._oid(item) == target for item in later_items)

    @classmethod
    def _module_to_next_module(cls, module):
        next_module = {
            "name": module.get("name"),
            "description": module.get("description"),
            "topics": [],
        }
        for topic in module.get("topics", []):
            next_module["topics"].append(
                {
                    "name": topic.get("name"),
                    "description": topic.get("description"),
                    "resources": list(topic.get("resources", [])),
                }
            )
        return next_module

    @classmethod
    def _module_name_in_next(cls, next_modules, module_name):
        return any(module.get("name") == module_name for module in next_modules)

    @classmethod
    def _load_path_and_journey(cls, path_id, token, breadcrumb):
        cls._check_permission(token, "mutate")
        cls._validate_object_id(path_id, "path_id")

        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        path = mongo.get_document(config.PATH_COLLECTION_NAME, path_id)
        if path is None:
            raise HTTPNotFound(f"Path {path_id} not found")

        journey = cls.get_my_journey(token, breadcrumb)
        journey_id = str(journey["_id"])
        later_items = journey.get("later", [])

        if not cls._path_id_in_later(later_items, path_id):
            raise HTTPNotFound(f"Path {path_id} not found in journey later scope")

        return mongo, config, path, journey, journey_id, later_items

    @classmethod
    def promote_path_to_next(cls, path_id, token, breadcrumb):
        try:
            mongo, config, path, journey, journey_id, later_items = (
                cls._load_path_and_journey(path_id, token, breadcrumb)
            )

            path_modules = path.get("modules", [])
            if not path_modules:
                raise HTTPBadRequest(f"Path {path_id} has no modules to promote")

            next_modules = copy.deepcopy(journey.get("next", []))
            for module in path_modules:
                next_modules.append(cls._module_to_next_module(module))

            target_path_oid = cls._oid(path_id)
            updated_later = [
                item
                for item in later_items
                if cls._oid(item) != target_path_oid
            ]

            set_data = {
                "next": next_modules,
                "later": updated_later,
                "saved": breadcrumb,
            }
            encode_document(set_data, ["resources", "later"], [])
            updated = mongo.update_document(
                config.JOURNEY_COLLECTION_NAME,
                document_id=journey_id,
                set_data=set_data,
            )

            logger.info(f"Promoted path {path_id} to next for journey {journey_id}")
            return updated
        except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error promoting path {path_id} to next: {e}")
            raise HTTPInternalServerError(f"Failed to promote path {path_id} to next")

    @classmethod
    def promote_module_to_next(cls, path_id, module_name, token, breadcrumb):
        try:
            mongo, config, path, journey, journey_id, _later_items = (
                cls._load_path_and_journey(path_id, token, breadcrumb)
            )

            if not module_name:
                raise HTTPBadRequest("module_name is required")

            path_module = None
            for module in path.get("modules", []):
                if module.get("name") == module_name:
                    path_module = module
                    break

            if path_module is None:
                raise HTTPNotFound(
                    f"Module {module_name!r} not found in path {path_id}"
                )

            next_modules = copy.deepcopy(journey.get("next", []))
            if cls._module_name_in_next(next_modules, module_name):
                raise HTTPBadRequest(
                    f"Module {module_name!r} is already present in journey next scope"
                )

            next_modules.append(cls._module_to_next_module(path_module))

            set_data = {
                "next": next_modules,
                "saved": breadcrumb,
            }
            encode_document(set_data, ["resources"], [])
            updated = mongo.update_document(
                config.JOURNEY_COLLECTION_NAME,
                document_id=journey_id,
                set_data=set_data,
            )

            logger.info(
                f"Promoted module {module_name!r} from path {path_id} "
                f"to next for journey {journey_id}"
            )
            return updated
        except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(
                f"Error promoting module {module_name!r} from path {path_id} to next: {e}"
            )
            raise HTTPInternalServerError(
                f"Failed to promote module {module_name!r} from path {path_id} to next"
            )
```
