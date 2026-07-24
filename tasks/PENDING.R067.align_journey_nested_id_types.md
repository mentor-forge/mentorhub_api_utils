# R067 – Align Journey nested id types to the schema (drop the `_normalize_id` bridge)

**Status**: Pending  
**Type**: Defect  
**Depends On**: `none`  
**Description**: `JourneyService` stores several nested reference fields as **strings** even though the live Journey schema declares every id field as a 24-hex `ObjectId` identifier. This forces a defensive `_normalize_id` string-coercion bridge and mixed BSON/string typing (the smell Mike flagged in the R062–R066 review). Additionally, `advance_resource` writes the resource **name** into `now[].resource_id` (`resource.get("name", ...)`) and `_find_now_entry` matches by name — both diverge from the schema, which requires an id there. Align the stored types to the schema by encoding id fields to `ObjectId` at the `MongoIO` write boundary via `encode_document`, switch `now[].resource_id` to the id, then remove `_normalize_id` and compare ids consistently. Split out from PR #23 because it changes **stored data shape** and the mentee advance/complete flow semantics (and may need a data migration); kept separate so the harvest release (`0.6.0`) stays low-risk.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — **MongoDB ObjectId handling (inbound vs outbound)** section (added in PR #23)
- `tasks/_PLANNING.md` — esp. **MongoDB dictionary schemas** (fetch the *definitive* schema from the running configurator, not repo YAML) and **MongoDB access**
- `tasks/_ORCHESTRATE.md`
- `api_utils/services/journey_service.py` — `_normalize_id`, `_clone_template`, `_module_to_next_module`, `advance_resource`, `complete_resource`, `promote_path_to_next`, `promote_module_to_next`, `get_journey_progress`
- `api_utils/mongo_utils/encode_properties.py` — `encode_document`
- `api_utils/mongo_utils/mongo_io.py` — note `get_documents(match=...)` does **not** coerce match values
- `tests/services/test_journey_service.py`

### Authoritative schema — fetched live (do NOT trust repo YAML)

Per `_PLANNING.md`, the definitive schema comes from the **running configurator**,
not the repo YAML. This was confirmed on 2026-07-24 with the DB up
(`pipenv run db`):

```bash
curl -s "http://localhost:8383/api/configurations/json_schema/Journey.yaml/latest/" -H "accept: application/json"
```

The live schema reports **every** id field as a 24-hex identifier
(`"pattern":"^[0-9a-fA-F]{24}$","type":"string"` on the wire = BSON `ObjectId`):

| Field | Live schema | BSON |
|-------|-------------|------|
| `_id`, `profile_id` | 24-hex identifier | `ObjectId` |
| `library[].resource_id` | 24-hex identifier | `ObjectId` |
| `library[].started`, `library[].completed` | `date-time` | `datetime` |
| `next[].topics[].resources[]` | 24-hex identifier | `ObjectId` |
| `later[]` | 24-hex identifier | `ObjectId` |
| `now[].resource_id` | **24-hex identifier** | **`ObjectId`** |

> **Caution:** the checked-in `mentorhub_mongodb_api/configurator/dictionaries/Journey.0.1.0.yaml`
> is stale (that local checkout was 8 commits behind `origin/main`) and wrongly
> lists `now[].resource_id` as `word`. Ignore it — trust the live curl. There is
> **no `word` id field and no `resource_id` key-name collision**; encoding is
> uniform across all id fields.

### `now[].resource_id` currently holds a name (code bug vs schema)

The live schema requires `now[].resource_id` to be an id, but the code writes the
resource **name**: `advance_resource` sets `"resource_id": resource.get("name",
resource_id)` and `_find_now_entry` matches by name. This must change to store
the **id** and match by id. Verify existing `now` data (it may contain names) and
plan a migration if needed before flipping the write. Because `resource_id` now
means the same thing everywhere, a single `encode_document(set_data, ["_id",
"profile_id", "resource_id", "resources", "later"], ["added", "started",
"completed"])`-style pass (scoped to the fields actually present in each write)
is safe — no `ObjectId(<name>)` hazard.

## Goals

- All id fields are stored as BSON `ObjectId` per the live Journey schema:
  - `next[].topics[].resources[]`, `library[].resource_id`, `later[]`, and `now[].resource_id` are written as `ObjectId` (encoded at the `MongoIO` write boundary in `_module_to_next_module`/`promote_*`, `complete_resource`, and `advance_resource`).
  - `advance_resource` stores the resource **id** in `now[].resource_id` (not the name), and `_find_now_entry` matches by id.
  - `library[].started`/`completed`/`now[].added` remain `datetime` where written.
- Encoding is done with `encode_document` (scoped to the id/date fields present in each write); no `ObjectId(<name>)` hazard since all `resource_id` occurrences are ids.
- `_normalize_id` is **removed**; id comparisons operate on consistent types (encode the inbound id once, then compare `ObjectId == ObjectId`).
- No behavioral regression in `get_my_journey`, `advance_resource`, `complete_resource`, `promote_path_to_next`, `promote_module_to_next`, or `get_journey_progress`.
- Backward compatibility with existing Journey data is considered — `now[].resource_id` may currently hold names — a one-off data migration may be needed; document the decision in Execution Notes.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db` — required (integration `MongoIO` tests + optional live schema fetch)
- `pipenv run test` — full suite green; **add tests that assert stored element types** (e.g. promoted `next` resources, completed `library[].resource_id`, and `now[].resource_id` are all `ObjectId`); update the existing `advance`/`complete` mocks that currently use the resource *name* as `now[].resource_id`
- `pipenv run lint`
- `pipenv run build`
- Consider an E2E pass (`pipenv run dev` + `pipenv run e2e`) covering advance → complete and promote flows, since stored shapes change.

## Outputs

- `api_utils/services/journey_service.py` — encode id fields at write boundaries; remove `_normalize_id`; consistent id comparisons
- `tests/services/test_journey_service.py` — update/add type-asserting tests for the mutation flows
- (If a data migration is warranted) `tasks/AS_NEEDED.*.md` — a migration task; otherwise document why not in Execution Notes

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
