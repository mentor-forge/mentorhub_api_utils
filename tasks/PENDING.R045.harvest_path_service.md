# R045 – Harvest PathService into api_utils.services

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R044_harvest_resource_service`  
**Description**: Move `PathService` from `mentorhub_mentee_api` into `api_utils.services.path_service` with unit tests.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

- Source: `../mentorhub_mentee_api/src/services/path_service.py`
- Source tests: `../mentorhub_mentee_api/test/services/test_path_service.py`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `../mentorhub_mentee_api/src/services/path_service.py`
- `../mentorhub_mentee_api/test/services/test_path_service.py`
- `api_utils/services/resource_service.py`

**PathService surface** (mentee API — read-only):

- `get_paths(token, breadcrumb)` — `MongoIO.get_documents` sorted by `name` ascending
- `get_path(path_id, token, breadcrumb)` — loads path, collects nested resource IDs from `modules[].topics[].resources[]`, calls `ResourceService.get_resources_by_ids`, merges summaries into enriched path document
- Helpers: `_collect_resource_ids`, `_enrich_path_resources`
- Auth-only `_check_permission` placeholder

**Import changes**:

- Replace `from src.services.resource_service import ResourceService` with `from api_utils.services.resource_service import ResourceService` (lazy inside `get_path`).

**Note**: `mentorhub_mentor_api` `PathService` adds `create_path`, `update_path` (mentor/admin RBAC), optional name filter, and returns raw documents without resource enrichment. Downstream mentor refactor may subclass or wrap the shared service for write operations and RBAC overrides.

## Goals

- `api_utils.services.path_service.PathService` matches mentee API read + enrichment behavior.
- `get_path` enriches nested `resources` with `_id`, `name`, `description` summaries.
- Unit tests ported to `tests/services/test_path_service.py` (including enrichment and archived-resource visibility cases).
- `api_utils/services/__init__.py` exports `PathService`.

## Testing Expectations

- `pipenv run test tests/services/test_path_service.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/services/path_service.py`
- `api_utils/services/__init__.py` — export `PathService`
- `tests/services/test_path_service.py`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
