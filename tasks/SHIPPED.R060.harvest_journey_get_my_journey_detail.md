# R060 – Harvest Journey GET profile enrichment into JourneyService

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R059_harvest_journey_promote_mutations`  
**Description**: Add `JourneyService.get_my_journey_detail(token, breadcrumb)` — call `get_my_journey`, load Profile via MongoIO, return journey plus embedded read-only `profile`. Add `"profile"` to `RESTRICTED_UPDATE_FIELDS`. Port unit tests. GET enrichment only; mutation paths unchanged.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Source service: `../mentorhub_mentee_api/src/services/journey_detail_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_journey_detail_service.py`
- Target: `api_utils/services/journey_service.py`
- Target tests: `tests/services/test_journey_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/SHIPPED.R046.harvest_journey_service.md`
- `tasks/SHIPPED.R059.harvest_journey_promote_mutations.md` — promote harvest (serial predecessor)
- `../mentorhub_mentee_api/src/services/journey_detail_service.py`
- `../mentorhub_mentee_api/test/services/test_journey_detail_service.py`
- `../mentorhub_mentee_api/tasks/ISSUE.mentorhub_api_utils.journey_get_profile_enrichment.md` — design summary
- `../mentorhub_mentee_api/src/routes/journey_routes.py` — route-level PATCH `profile` guard (to be superseded by `RESTRICTED_UPDATE_FIELDS` on adopt)
- `api_utils/services/journey_service.py` — existing `get_my_journey`, `RESTRICTED_UPDATE_FIELDS`, mutation methods
- `api_utils/config/config.py` — `PROFILE_COLLECTION_NAME`, `JOURNEY_COLLECTION_NAME`

### Design (read-time composite)

Mirrors the **ResourceDetail** pattern: the MongoDB Journey document is unchanged; `profile` is **not** persisted on the Journey collection.

- **`get_my_journey_detail(token, breadcrumb)`**:
  - Require `profile_id` on token (`400` if missing).
  - Call existing `get_my_journey(token, breadcrumb)`.
  - Load Profile via `MongoIO.get_document(config.PROFILE_COLLECTION_NAME, profile_id)`.
  - Missing Profile → `HTTPNotFound`.
  - Return `{**journey, "profile": profile}`.

### Mutation contract (unchanged)

- `get_my_journey`, `update_journey`, `advance_resource`, `complete_resource`, and promote methods (`promote_path_to_next`, `promote_module_to_next`) continue to return **plain Journey documents without `profile`**.

### RESTRICTED_UPDATE_FIELDS

Add `"profile"` to the existing list so PATCH bodies cannot persist a synthetic profile field:

```python
RESTRICTED_UPDATE_FIELDS = [
    "_id",
    "profile_id",
    "created",
    "saved",
    "library",
    "now",
    "next",
    "profile",  # read-time composite only; not stored on Journey
]
```

## Goals

- `JourneyService.get_my_journey_detail` matches mentee API local `JourneyDetailService` behavior.
- `"profile"` added to `RESTRICTED_UPDATE_FIELDS`; `update_journey` rejects PATCH bodies containing `profile`.
- Unit tests from mentee API ported to `tests/services/test_journey_service.py`.
- No changes to mutation return shapes or promote behavior from R059.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run test tests/services/test_journey_service.py` — includes new detail coverage and `profile` PATCH rejection if covered elsewhere in file
- `pipenv run test`
- `pipenv run lint`
- `pipenv run build`

## Outputs

- `api_utils/services/journey_service.py` — add `get_my_journey_detail`; extend `RESTRICTED_UPDATE_FIELDS`

- `tests/services/test_journey_service.py` — add ported detail tests

The agent must not update files outside this list.

## Execution Notes

- Added `get_my_journey_detail`; extended `RESTRICTED_UPDATE_FIELDS` with `"profile"`.
- Ported 4 detail unit tests plus `test_update_journey_rejects_profile_field`.
- `pipenv run test`: 196 passed; `pipenv run build`: `api_utils-0.5.1` succeeded.
