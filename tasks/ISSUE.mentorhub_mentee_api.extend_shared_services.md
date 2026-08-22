# Extend shared services in Mentee API (Note, Aggregation, Path, Event)

> **Cross-repo issue artifact.** Paste-ready description for
> **`mentorhub_mentee_api`**. Not orchestrated from `mentorhub_api_utils`.
> **Blocked on**: `api-utils>=1.0.0` (R075–R082) **and** `ISSUE.journey_api.md`
> (same wave — `complete_resource` calls local `AggregationService.add_completion`).

## Summary

Mentee **controls** Journey, Rating, and Note; it **creates** Event; it
**consumes** Resource and Path (`architecture.yaml`). After the api_utils
data-boundary split, recreate `src/services/` as subclasses. Routes must import
those subclasses, not `api_utils.services` directly.

Journey subclass source: **`ISSUE.journey_api.md`**. This issue covers the rest.

## Pin

- `api-utils==1.0.0` (or the R080 release) via `pipenv run install`.

## Layout

```
src/services/__init__.py
src/services/journey_service.py      # ISSUE.journey_api.md
src/services/note_service.py         # create_note
src/services/aggregation_service.py  # add_hit, add_completion, get_aggregation_detail
src/services/path_service.py         # enrich get_path
src/services/event_service.py        # optional thin subclass; create_event stays on shared
src/services/resource_service.py     # optional thin subclass; GETs stay on shared
```

```python
from api_utils.services import NoteService as SharedNoteService

class NoteService(SharedNoteService):
    @classmethod
    def create_note(cls, data, token, breadcrumb):
        ...
```

## Routes

| File | Today | After |
|------|-------|-------|
| `src/routes/journey_routes.py` | `from api_utils.services import JourneyService` | `from src.services.journey_service import JourneyService` |
| `src/routes/note_routes.py` | `from api_utils.services import NoteService` | local subclass (`create_note`) |
| `src/routes/aggregation_routes.py` | `AggregationService.get_aggregation_detail` | local subclass |
| `src/routes/path_routes.py` | shared `get_path` (enriched) | local subclass that enriches |
| `src/routes/event_routes.py` | shared `create_event` | local subclass **or** shared EventService (global POST is allowed on shared; still prefer a local subclass so every route uses `src.services`) |
| `src/routes/resource_routes.py` | shared GETs | local subclass that inherits GETs |

## Harvest-back: `NoteService.create_note`

Removed from api_utils in R079. `ID_PROPERTIES = ["_id", "resource_id", "profile_id"]`.

```python
@classmethod
def create_note(cls, data, token, breadcrumb):
    try:
        cls._check_permission(token, "create")
        if "_id" in data:
            del data["_id"]
        encode_document(data, ["_id", "resource_id", "profile_id"], [])
        data["created"] = breadcrumb
        data["saved"] = breadcrumb
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        note_id = mongo.create_document(config.NOTE_COLLECTION_NAME, data)
        if "_id" not in data:
            from bson import ObjectId
            data["_id"] = ObjectId(note_id)
        return data
    except HTTPForbidden:
        raise
    except Exception as e:
        raise HTTPInternalServerError(f"Failed to create note: {e}")
```

Override `_check_permission` for `create` if Mentee-only POST is required.

## Harvest-back: Path enrich

Shared `get_path` returns the raw document. Move these helpers onto the Mentee
`PathService` subclass and wrap `get_path`:

- `_collect_resource_ids(path)`
- `_enrich_path_resources(path, resource_summaries)`
- `get_path`: `path = super().get_path(...)`; `ResourceService.get_resources_by_ids`; return enriched

Copy bodies from `api_utils/services/path_service.py` before R079 (classmethod/`cls`).

## Harvest-back: Aggregation mutate + enrich

Shared keeps `get_aggregation_for_resource` (no create). Move to Mentee subclass:

- `_get_or_create_aggregation`, `_new_aggregation_document` (keep `_find_aggregation` / `_resource_object_id` via `super()` if they remain on the parent; if R079 leaves find helpers on the parent, call them)
- `add_hit`, `add_completion` (create_note via **local** `NoteService`)
- `get_aggregation_detail` — get-or-create + `NoteService.list_all_notes_for_resource` → `{aggregation, notes}`

Copy `add_hit` / `add_completion` / `_get_or_create_aggregation` from
`api_utils/services/aggregation_service.py` before R079. Duration helpers
(`_parse_iso_duration`, `_add_durations`, …) stay on the parent if still
present; otherwise copy them too.

`add_completion` currently does `from api_utils.services.note_service import NoteService` —
change to `from src.services.note_service import NoteService`.

## Harvest-back: Resource GET composite

Shared `get_resource` returns the raw document. Move the BFF composite onto the
Mentee `ResourceService` subclass and wrap `get_resource`:

```python
@classmethod
def get_resource(cls, resource_id, token, breadcrumb):
    resource = super().get_resource(resource_id, token, breadcrumb)
    aggregation = AggregationService.get_aggregation_for_resource(
        resource_id, token, breadcrumb
    )
    notes = NoteService.list_all_notes_for_resource(
        resource_id, token, breadcrumb
    )
    return {
        "resource": resource,
        "aggregation": aggregation,
        "notes": notes,
    }
```

Use **local** `AggregationService` and `NoteService` subclasses for the enrich
calls.

## Event

`EventService.create_event` remains on shared (global POST). Provide a local
`class EventService(SharedEventService):` even if empty so routes stay consistent.

Link events previously called shared `AggregationService.add_hit` after create;
that side effect was removed from shared in R079. Override `create_event` on
the Mentee subclass to call local `AggregationService.add_hit` when
`type == EVENT_TYPE_LINK` and `token.resource_id` is present (copy the block
removed from `api_utils/services/event_service.py`).

## Inbound RBAC (F-UA12)

Shared GETs already apply **outbound** filters. Add **inbound** `_check_permission` only on writes:

| Subclass method | Who may call (non-admin) |
|-----------------|--------------------------|
| `NoteService.create_note` | mentee role; stamp/require `profile_id == token.profile_id` |
| `AggregationService.add_hit` | any authenticated (current) |
| `AggregationService.add_completion` | mentee role (current) |
| `JourneyService` writes | see `ISSUE.journey_api.md` |
| `EventService.create_event` | any authenticated (global create) |

Admin is root. Do not 403 on GET in these subclasses.

## Acceptance

- No route imports `api_utils.services` service classes (filter/order constants may still come from api_utils).
- `src/services/` subclasses shared classes; Journey code matches `ISSUE.journey_api.md`.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`, `pipenv run e2e`.
