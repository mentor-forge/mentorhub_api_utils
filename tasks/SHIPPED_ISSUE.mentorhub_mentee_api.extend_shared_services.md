Please create @_PLANNING.MD tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_mentee_api/issues/27

# F-EA13: Extend shared services in Mentee API (Note, Aggregation, Path, Event)

Paired with **F-EA12** (`SHIPPED_ISSUE.journey_api.md`). That issue owns the
`api-utils==1.0.0` pin; **ship both in the same PR**. This issue covers every
Mentee subclass except Journey.

## Summary

Mentee **controls** Journey, Rating, and Note; it **creates** Event; it
**consumes** Resource and Path (`architecture.yaml`). Today this repo has **no**
`src/services/` — routes import `api_utils.services` directly:

| Route | Shared call that 1.0.0 removed or flattened |
|-------|-----------------------------------------------|
| `note_routes.py` POST | `NoteService.create_note` |
| `aggregation_routes.py` GET | `AggregationService.get_aggregation_detail` |
| `path_routes.py` GET by-id | enriched `get_path` (1.0.0 returns the raw Path) |
| `resource_routes.py` GET by-id | composite `{resource, aggregation, notes}` (R083 flattened to a plain document) |
| `event_routes.py` POST | `create_event` remains shared; restore link → `add_hit` on the subclass |
| `journey_routes.py` | see F-EA12 |

After the 1.0.0 data-boundary split, recreate `src/services/` as subclasses.
Routes must import those subclasses, not `api_utils.services` directly.

Journey subclass source: **`SHIPPED_ISSUE.journey_api.md`**.

## Pin

- Already set to `api-utils==1.0.0` by F-EA12 in this same PR.
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed).

## Layout

```
src/services/__init__.py
src/services/journey_service.py      # SHIPPED_ISSUE.journey_api.md
src/services/note_service.py         # create_note
src/services/aggregation_service.py  # add_hit, add_completion, get_aggregation_detail
src/services/path_service.py         # enrich get_path
src/services/event_service.py        # thin subclass; restore link add_hit
src/services/resource_service.py     # override get_resource with BFF composite
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
| `src/routes/path_routes.py` | shared `get_path` (raw in 1.0.0) | local subclass that enriches |
| `src/routes/event_routes.py` | shared `create_event` | local subclass so every route uses `src.services` |
| `src/routes/resource_routes.py` | shared GETs (plain document in 1.0.0) | local subclass that restores the composite |

## Harvest-back source

Last full shared copies (classmethod form) live at git commit **`9af2886`**
in `mentorhub_api_utils` (R075, before R079 strip):

- `api_utils/services/note_service.py` — `create_note`
- `api_utils/services/aggregation_service.py` — duration helpers, `_get_or_create_aggregation`, `add_hit`, `add_completion`, `get_aggregation_detail`
- `api_utils/services/path_service.py` — `_collect_resource_ids`, `_enrich_path_resources`, enriched `get_path`
- `api_utils/services/event_service.py` — link → `AggregationService.add_hit`
- `api_utils/services/resource_service.py` — composite `get_resource` (removed later in R083)

Duration helpers (`_parse_iso_duration`, `_format_iso_duration`, `_add_durations`)
are **not** on the 1.0.0 parent — copy them onto the Mentee `AggregationService`
subclass.

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

Copy bodies from `9af2886:api_utils/services/path_service.py`.

## Harvest-back: Aggregation mutate + enrich

Shared keeps `get_aggregation_for_resource` (no create) plus `_find_aggregation`
/ `_resource_object_id`. Move to the Mentee subclass:

- `_get_or_create_aggregation`, `_new_aggregation_document`
- duration helpers (not on the parent)
- `add_hit`, `add_completion` (create_note via **local** `NoteService`)
- `get_aggregation_detail` — get-or-create + `NoteService.list_all_notes_for_resource` → `{aggregation, notes}`

`add_completion` currently did `from api_utils.services.note_service import NoteService` —
change to `from src.services.note_service import NoteService`.

## Harvest-back: Resource GET composite

Shared `get_resource` (R083) returns the raw document. Restore the BFF composite
on the Mentee `ResourceService` subclass:

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
calls. List GET stays inherited (`get_resources`) — do **not** POST Resource
here (Mentor **controls** Resource).

## Event

`EventService.create_event` remains on shared (global POST). Provide a local
`class EventService(SharedEventService):` so routes stay consistent.

Override `create_event` on the Mentee subclass to call local
`AggregationService.add_hit` when `type == EVENT_TYPE_LINK` and
`token.resource_id` is present (copy the block from
`9af2886:api_utils/services/event_service.py`).

## Inbound RBAC (F-UA12)

Shared GETs already apply **outbound** filters. Add **inbound** `_check_permission` only on writes:

| Subclass method | Who may call (non-admin) |
|-----------------|--------------------------|
| `NoteService.create_note` | mentee role; stamp/require `profile_id == token.profile_id` |
| `AggregationService.add_hit` | any authenticated (current) |
| `AggregationService.add_completion` | mentee role (current) |
| `JourneyService` writes | see `SHIPPED_ISSUE.journey_api.md` |
| `EventService.create_event` | any authenticated (global create) |

Admin is root. Do not 403 on GET in these subclasses.

## Shared GET routes

Replace duplicated GET handlers with `create_*_get_routes(LocalService)` from
`api_utils` (`api_utils.routes.shared_get_routes`). Add control POST/PATCH on
the returned blueprint. List GET body is a JSON array; pagination is
`offset`/`size` request headers only (no cursor, no `X-Pagination-*`).

Mentee **consumes** Resource and Path — GET only, no create POST.

| Route module | Factory | Notes |
|--------------|---------|-------|
| `resource_routes.py` | `create_resource_get_routes(ResourceService)` | list + by-id; by-id uses subclass composite |
| `path_routes.py` | `create_path_get_routes(PathService)` | list + by-id; by-id uses subclass enrich |
| `note_routes.py` | `create_note_get_routes(NoteService)` | list only; requires `resource_id` query; add POST `create_note` |
| `event_routes.py` | `create_event_get_routes(EventService)` | list only; add POST `create_event` |
| `journey_routes.py` | `create_journey_get_routes(JourneyService)` | by-id only — keep local `GET ""` get-or-create |
| `aggregation_routes.py` | `create_aggregation_get_routes(AggregationService)` | by-id only (plain doc). Keep a **local** `GET` that calls `get_aggregation_detail` if OpenAPI still returns `{aggregation, notes}` |

## Acceptance

- No route imports `api_utils.services` service classes (filter/order constants may still come from api_utils).
- `src/services/` subclasses shared classes; Journey code matches `SHIPPED_ISSUE.journey_api.md`.
- Same PR as F-EA12 (`api-utils==1.0.0`).
- `pipenv run test`, `pipenv run lint`, `pipenv run build`, `pipenv run e2e`.
