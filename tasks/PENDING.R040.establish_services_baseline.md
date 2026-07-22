# R040 – Establish `api_utils.services` + `list_query` baseline

**Status**: Pending  
**Task Type**: Feature  
**Run Mode**: Sequential  <!-- options: Sequential | Run as needed -->

## Goal

Reconcile this working tree with the published `api-utils` `0.5.x` baseline so
the shared read-service surface already consumed by `mentorhub_mentor_api`
exists locally and can be extended by later harvest tasks (R050–R120).

At authoring time the local tree is `version = "0.2.4"` and is **missing**:

- the `api_utils/services/` package (Resource/Event/Path list-read services and
  their `*_LIST_FILTERS` / `*_LIST_ORDER` specs),
- `api_utils/mongo_utils/list_query.py`
  (`DEFAULT_OFFSET`, `DEFAULT_SIZE`, `build_match_filter`, `build_sort_by`,
  `execute_list_query`),
- `skip` / `limit` support on `MongoIO.get_documents(...)`.

Yet `mentorhub_mentor_api` pins `api-utils==0.5.1` and already imports all of
the above. Everything the harvest needs from `Config` (all `*_COLLECTION_NAME`
keys and `ROLE_MENTOR`/`ROLE_ADMIN`) is **already present** locally, so no config
work is required.

## Decision point (resolve before implementing)

Choose how to obtain the baseline and record the decision in **Implementation
notes**:

- **(a) Recommended — sync the published `0.5.x` source.** Fetch/merge the
  branch/tag that produced `api-utils==0.5.1` so `services/` + `list_query` land
  as authored upstream, then continue on the harvest feature branch.
- **(b) Fallback — rebuild the baseline** from the mentor delegating wrappers
  (`mentorhub_mentor_api/src/services/{resource,event,path}_service.py`) if the
  `0.5.x` source is unavailable, reproducing `get_resources`/`get_events`/
  `get_paths` and the filter/order specs exactly as those wrappers expect them.

## Context / Input files

Read before implementation:

- `mentorhub_api_utils/README.md`
- `mentorhub_api_utils/pyproject.toml`
- `mentorhub_api_utils/api_utils/__init__.py`
- `mentorhub_api_utils/api_utils/mongo_utils/mongo_io.py`
- `mentorhub_api_utils/api_utils/config/config.py`
- `mentorhub_mentor_api/src/services/resource_service.py` (consumer contract)
- `mentorhub_mentor_api/src/services/event_service.py` (consumer contract)
- `mentorhub_mentor_api/src/services/path_service.py` (consumer contract)
- `mentorhub_mentor_api/tasks/ISSUE.mentorhub_api_utils.harvest_mentor_services.md`
- `mentorhub/DeveloperEdition/standards/api_standards.md`

## Requirements

- Create the `api_utils/services/` package exporting `ResourceService`,
  `EventService`, `PathService` with the **list reads** consumed by the mentor
  wrappers, plus the re-exported specs `RESOURCE_LIST_FILTERS`/`_ORDER`,
  `EVENT_LIST_FILTERS`/`_ORDER`, `PATH_LIST_FILTERS`/`_ORDER`.
- Create `api_utils/mongo_utils/list_query.py` exposing `DEFAULT_OFFSET`,
  `DEFAULT_SIZE`, `build_match_filter`, `build_sort_by`, `execute_list_query`
  with the exact signatures the mentor `PlanService`/`ResourceService` call.
- Extend `MongoIO.get_documents(...)` to accept optional `skip` and `limit`
  (used by `execute_list_query` and by scoped reads such as
  `get_encounters_for_mentee`). Preserve existing `match/project/sort_by`
  behavior and defaults.
- Route all storage through `MongoIO` — no direct PyMongo in service code.
- Keep behavior identical to `0.5.1` as observed by the mentor consumers; this
  task adds no new domain behavior (that is R050+).

## Files to modify / create

- **Create**: `api_utils/services/__init__.py`
- **Create**: `api_utils/services/resource_service.py`
- **Create**: `api_utils/services/event_service.py`
- **Create**: `api_utils/services/path_service.py`
- **Create**: `api_utils/mongo_utils/list_query.py`
- **Modify**: `api_utils/mongo_utils/mongo_io.py` (add `skip`/`limit`)
- **Modify**: `api_utils/__init__.py` (re-export as appropriate)
- **Create**: `tests/services/` unit/integration tests for the list reads and
  `list_query` helpers; `tests/mongo_utils/` coverage for `skip`/`limit`.

## Testing expectations

- `pipenv run db` (MongoIO integration tests need a running MongoDB).
- `pipenv run test` — unit + MongoIO integration green.
- `pipenv run lint` — `black --check` clean.
- `pipenv run build` — package builds/imports cleanly.
- Sanity import check: `from api_utils.services import ResourceService, EventService, PathService`
  and `from api_utils.mongo_utils.list_query import DEFAULT_OFFSET, DEFAULT_SIZE, build_match_filter, build_sort_by, execute_list_query` both succeed.

## Packaging / build checks

- `pipenv run test`, `pipenv run lint`, `pipenv run build` all pass.
- Version bump for the whole feature is deferred to **R140** (single bump
  before the PR).

## Dependencies / Ordering

- Blocker for **all** later harvest tasks (R050–R130). Must run first.

## Change control checklist

- [ ] Reviewed all **Context / Input files**.
- [ ] Recorded the baseline-source decision (a/b) in Implementation notes.
- [ ] Created `api_utils/services/` list-read package + specs.
- [ ] Created `api_utils/mongo_utils/list_query.py`.
- [ ] Added `skip`/`limit` to `MongoIO.get_documents`.
- [ ] Added tests; `pipenv run test` green.
- [ ] `pipenv run lint` / `pipenv run build` clean.
- [ ] Scoped commit referencing this task ID.

## Implementation notes (to be updated by the agent)

_(reserved for the execution agent: baseline-source decision, plan, commands, results, follow-ups)_
