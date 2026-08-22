# Extend shared services in Mentor API (inherit GETs; keep control mutations)

> **Cross-repo issue artifact.** Paste-ready description for
> **`mentorhub_mentor_api`**. Not orchestrated from `mentorhub_api_utils`.
> **Blocked on**: `api-utils>=1.0.0` (R075–R082).

## Summary

Mentor **controls** Resource, Path, Plan, Encounter; **creates** Event;
**consumes** Profile (`architecture.yaml`). Today several local services
*compose* shared GETs (`SharedResourceService.get_resources`). After 1.0.0 they
must **extend** the shared class. Routes already import `src.services` — keep
that; do not switch routes to `api_utils.services`.

Shared Profile no longer includes Mentor Dashboard enrich (`get_profiles`
cards, composite `get_profile`, `get_profile_properties`). Those stay local
on the Mentor `ProfileService` subclass (they already exist in
`src/services/profile_service.py`).

## Pin

- `api-utils==1.0.0` via `pipenv run install`.

## Convert composition → inheritance

Replace:

```python
from api_utils.services import ResourceService as SharedResourceService

class ResourceService:
    def get_resources(...):
        return SharedResourceService.get_resources(...)
```

with:

```python
from api_utils.services import ResourceService as SharedResourceService

class ResourceService(SharedResourceService):
    # inherit get_resources / get_resource / get_resources_by_ids
    @classmethod
    def create_resource(cls, data, token, breadcrumb):
        ...
    @classmethod
    def update_resource(cls, resource_id, data, token, breadcrumb):
        ...
```

Apply to `ResourceService`, `PathService`, `EventService`, and any other
module that delegates list reads. Convert `@staticmethod` to `@classmethod`
when touching a file.

| Local service | Inherit from shared | Keep local |
|---------------|---------------------|------------|
| `ResourceService` | GETs + list filters | `create_resource`, `update_resource` |
| `PathService` | `get_paths`; raw `get_path` | `create_path`, `update_path`; **do not** re-add mentee resource-summary enrich |
| `PlanService` | `get_plans`, `get_plan` | `create_plan`, `update_plan` (R079 removes these from api_utils — keep the local copies) |
| `EncounterService` | GET helpers | `create_encounter` (agenda from Plan), `update_encounter` (owner-or-admin) |
| `MenteeService` | read-only `get_mentee` (404 if missing) | restore create-if-missing **or** wrap GET: on 404 call `_default_document` + create; keep `update_mentee` |
| `ProfileService` | `get_profile_by_token`, shared `get_profile` / `get_profiles` / `create_profile` | rename dashboard methods if they collide (`get_dashboard` / `get_profile_detail` / `get_profile_properties`) **or** override `get_profiles` / `get_profile` with the current mentor enrich (routes must match OpenAPI) |
| `JourneyService` | `get_journey_progress` | delete local duplicate progress implementation; do **not** add Mentee mutations |
| `EventService` | `create_event`, `get_events` | drop local `create_event` duplicate unless mentor-specific encoding remains — prefer `super().create_event` |

If local `get_profile` / `get_profiles` names stay as the dashboard (OpenAPI
`ProfileDetail` / dashboard cards), override the shared methods in the subclass
so Mentor routes keep their contract. Customer/Admin will use the shared plain
GET/create via their own subclasses.

## Routes

Continue `from src.services.<x> import <Y>`. Re-export list filter/order
constants from the local module (already done for Resource/Path).

## Inbound RBAC (F-UA12)

Shared GETs apply **outbound** filters (including `status != archived` and
mentorship scope). Add **inbound** `_check_permission` on writes only:

| Subclass | Who may write (non-admin) |
|----------|---------------------------|
| `ResourceService` create/update | `ROLE_MENTOR` |
| `PathService` create/update | `ROLE_MENTOR` (update already required mentor/admin locally) |
| `PlanService` create/update | `ROLE_MENTOR` |
| `EncounterService` create | `ROLE_MENTOR`; update: owning mentor (`mentor_id`) or admin |
| `MenteeService` create-if-missing / update | `ROLE_MENTOR` |
| `EventService.create_event` | any authenticated |
| `ProfileService` dashboard overrides | read-only enrich; no Profile PATCH here (Customer **controls** Profile) |

Admin is root. Do not re-introduce 403-on-GET for “not a mentor” — outbound hides rows.

## Harvest-back: `PlanService` writes (removed from api_utils in R079)

```python
@classmethod
def _validate_update_data(cls, data):
    restricted_fields = ["_id", "created", "saved"]
    for field in restricted_fields:
        if field in data:
            raise HTTPForbidden(f"Cannot update {field} field")

@classmethod
def create_plan(cls, data, token, breadcrumb):
    try:
        cls._check_permission(token, "create")
        if "_id" in data:
            del data["_id"]
        data["created"] = breadcrumb
        data["saved"] = breadcrumb
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        plan_id = mongo.create_document(config.PLAN_COLLECTION_NAME, data)
        return plan_id
    except HTTPForbidden:
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to create plan: {e}")

@classmethod
def update_plan(cls, plan_id, data, token, breadcrumb):
    try:
        cls._check_permission(token, "update")
        cls._validate_update_data(data)
        restricted_fields = ["_id", "created", "saved"]
        set_data = {k: v for k, v in data.items() if k not in restricted_fields}
        set_data["saved"] = breadcrumb
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        updated = mongo.update_document(
            config.PLAN_COLLECTION_NAME, document_id=plan_id, set_data=set_data
        )
        if updated is None:
            raise HTTPNotFound(f"Plan {plan_id} not found")
        return updated
    except (HTTPForbidden, HTTPNotFound):
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to update plan {plan_id}")
```

## Harvest-back: `EncounterService` writes (removed from api_utils in R079)

Owner-or-admin write RBAC and agenda-from-plan logic move here. Read RBAC
(mentor-or-admin) stays on the shared parent.

```python
@classmethod
def _validate_update_data(cls, data):
    restricted_fields = ["_id", "created", "saved"]
    for field in restricted_fields:
        if field in data:
            raise HTTPForbidden(f"Cannot update {field} field")

@classmethod
def _build_agenda_from_plan(cls, plan):
    steps = plan.get("steps")
    if steps is None:
        steps = plan.get("checklist")
    if not steps:
        return []
    return [{"step": step, "checked": False} for step in steps]

@classmethod
def _check_permission_write(cls, token, operation, breadcrumb, encounter=None):
    from api_utils.services.profile_service import ProfileService
    config = Config.get_instance()
    roles = token.get("roles", []) or []
    if config.ROLE_ADMIN in roles:
        return
    if config.ROLE_MENTOR not in roles:
        raise HTTPForbidden("Mentor or admin role required to access encounter data")
    if encounter is not None:
        profile = ProfileService.get_profile_by_token(token, breadcrumb)
        caller_profile_id = profile.get("_id") if profile else None
        if caller_profile_id is None or str(caller_profile_id) != str(
            encounter.get("mentor_id")
        ):
            raise HTTPForbidden(
                "Only the owning mentor or an admin may update this encounter"
            )

@classmethod
def create_encounter(cls, data, token, breadcrumb):
    try:
        cls._check_permission_write(token, "create", breadcrumb)
        plan = PlanService.get_plan(data["plan_id"], token, breadcrumb)
        data["agenda"] = cls._build_agenda_from_plan(plan)
        if "_id" in data:
            del data["_id"]
        encode_document(data, ["mentor_id", "mentee_id", "plan_id"], [])
        data["created"] = breadcrumb
        data["saved"] = breadcrumb
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        encounter_id = mongo.create_document(config.ENCOUNTER_COLLECTION_NAME, data)
        return encounter_id
    except (HTTPForbidden, HTTPNotFound):
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to create encounter: {e}")

@classmethod
def update_encounter(cls, encounter_id, data, token, breadcrumb):
    try:
        cls._check_permission_write(token, "update", breadcrumb)
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        encounter = mongo.get_document(config.ENCOUNTER_COLLECTION_NAME, encounter_id)
        if encounter is None:
            raise HTTPNotFound(f"Encounter {encounter_id} not found")
        cls._check_permission_write(token, "update", breadcrumb, encounter=encounter)
        cls._validate_update_data(data)
        restricted_fields = ["_id", "created", "saved"]
        set_data = {k: v for k, v in data.items() if k not in restricted_fields}
        set_data["saved"] = breadcrumb
        updated = mongo.update_document(
            config.ENCOUNTER_COLLECTION_NAME,
            document_id=encounter_id,
            set_data=set_data,
        )
        if updated is None:
            raise HTTPNotFound(f"Encounter {encounter_id} not found")
        return updated
    except (HTTPForbidden, HTTPNotFound):
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to update encounter {encounter_id}")
```

## Harvest-back: `MenteeService` writes + create-if-missing (removed from R079)

Shared `get_mentee` is read-only (404 if missing). Restore create-if-missing
on GET and `update_mentee` on the Mentor subclass.

```python
RESTRICTED_FIELDS = ["_id", "created", "saved"]

@classmethod
def _validate_update_data(cls, data):
    for field in RESTRICTED_FIELDS:
        if field in data:
            raise HTTPForbidden(f"Cannot update {field} field")

@classmethod
def _default_document(cls, profile_object_id, breadcrumb):
    return {
        "profile_id": profile_object_id,
        "status": "active",
        "description": "",
        "focus": "",
        "homework": "",
        "notes": "",
        "created": breadcrumb,
        "saved": breadcrumb,
    }

@classmethod
def get_mentee(cls, profile_id, token, breadcrumb):
    try:
        cls._check_permission(token, "read")
        profile_object_id = cls._to_object_id(profile_id, "profile_id")
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        collection_name = cls._collection_name(config)
        existing = mongo.get_documents(
            collection_name, match={"profile_id": profile_object_id}
        )
        if existing:
            return existing[0]
        document = cls._default_document(profile_object_id, breadcrumb)
        mentee_id = mongo.create_document(collection_name, document)
        return mongo.get_document(collection_name, mentee_id)
    except (HTTPBadRequest, HTTPForbidden):
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to retrieve mentee for profile {profile_id}")

@classmethod
def update_mentee(cls, mentee_id, data, token, breadcrumb):
    try:
        cls._check_permission(token, "update")
        cls._validate_update_data(data)
        mentee_object_id = cls._to_object_id(mentee_id, "mentee_id")
        set_data = {k: v for k, v in data.items() if k not in RESTRICTED_FIELDS}
        set_data["saved"] = breadcrumb
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        collection_name = cls._collection_name(config)
        updated = mongo.update_document(
            collection_name,
            match={"_id": mentee_object_id},
            set_data=set_data,
        )
        if updated is None:
            raise HTTPNotFound(f"Mentee {mentee_id} not found")
        return updated
    except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to update mentee {mentee_id}")
```

## Tests

Repoint service tests at the subclass. Patch `src.services.*`. Remove tests
that assumed shared `ProfileService.get_profiles` returned dashboard cards.

## Acceptance

- Every domain service class subclasses the matching `api_utils.services` class.
- Control POST/PATCH remain in this repo; no route imports shared service classes.
- Dashboard enrich still works.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`, `pipenv run e2e`.

Supersedes `ISSUE.mentorhub_mentor_api.adopt_harvested_services.md` (that issue
deleted `src/services/` — the opposite of this split).
