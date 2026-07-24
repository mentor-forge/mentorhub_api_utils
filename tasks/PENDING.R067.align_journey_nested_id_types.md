# R067 – Align Journey nested id types to the schema (drop the `_normalize_id` bridge)

**Status**: Pending  
**Type**: Defect  
**Depends On**: `none`  
**Description**: `JourneyService` stores several nested reference fields as **strings** even though the Journey dictionary declares them as `identifier` (BSON `ObjectId`). This forces a defensive `_normalize_id` string-coercion bridge and mixed BSON/string typing (the smell Mike flagged in the R062–R066 review). Align the stored types to the schema by encoding id fields to `ObjectId` at the `MongoIO` write boundary via `encode_document`, then remove `_normalize_id` and compare ids consistently. Split out from PR #23 because it changes **stored data shape** and requires care around a `resource_id` key-name collision; kept separate so the harvest release (`0.6.0`) stays low-risk.

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

### Authoritative schema (fetch live before implementing)

Per `_PLANNING.md`, the definitive schema comes from the running configurator, not the repo YAML. With the DB up (`pipenv run db`):

```bash
curl -X GET "http://localhost:8383/api/configurations/json_schema/Journey.yaml/latest/" -H "accept: application/json"
```

At planning time the `Journey.0.1.0.yaml` dictionary declares:

| Field | Dictionary type | Intended BSON |
|-------|-----------------|---------------|
| `_id`, `profile_id` | `identifier` | `ObjectId` |
| `library[].resource_id` | `identifier` | `ObjectId` |
| `library[].started`, `library[].completed` | `date-time` | `datetime` |
| `next[].topics[].resources[]` | `identifier` | `ObjectId` |
| `later[]` | `identifier` | `ObjectId` |
| **`now[].resource_id`** | **`word`** | **string (the resource *name*, not an id)** |

### The `resource_id` key-name collision (read carefully)

`encode_document` encodes **by key name, recursively**. The key `resource_id`
means an **ObjectId** under `library` but a **word/name** under `now`. A naive
`encode_document(set_data, ["resource_id", ...])` would try `ObjectId("<a name>")`
for `now` entries and raise `ValueError`. So encoding must be **scoped per
sub-document** (encode the `library`/`next`/`later` subtrees, leave `now`
alone), or the `now` name field should be renamed upstream (out of scope here).

## Goals

- Identifier fields are stored as BSON `ObjectId` per the Journey schema:
  - `next[].topics[].resources[]`, `library[].resource_id`, `later[]` are written as `ObjectId` (encoded at the `MongoIO` write boundary in `_module_to_next_module`/`promote_*`, `complete_resource`, and `advance_resource`'s `next` rewrite).
  - `now[].resource_id` remains a **string name** (`word`); do not encode it.
  - `library[].started`/`completed` remain `datetime` where written.
- Encoding is done with `encode_document`, scoped to avoid the `resource_id` key collision (no `ObjectId(<name>)` attempts).
- `_normalize_id` is **removed**; id comparisons operate on consistent types (encode the inbound id once, compare `ObjectId == ObjectId`, and match names separately for `now`).
- No behavioral regression in `get_my_journey`, `advance_resource`, `complete_resource`, `promote_path_to_next`, `promote_module_to_next`, or `get_journey_progress`.
- Backward compatibility with any existing string-typed Journey data is considered (a one-off data migration may be needed; document the decision in Execution Notes).

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run db` — required (integration `MongoIO` tests + optional live schema fetch)
- `pipenv run test` — full suite green; **add tests that assert stored element types** (e.g. promoted `next` resources and completed `library[].resource_id` are `ObjectId`, `now[].resource_id` stays a name string)
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
