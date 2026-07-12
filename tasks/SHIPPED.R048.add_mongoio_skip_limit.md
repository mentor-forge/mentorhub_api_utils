# R048 – Add skip/limit to MongoIO.get_documents

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R047_export_services_public_api`  
**Description**: Extend `MongoIO.get_documents` with optional `skip` and `limit` parameters so list queries paginate in MongoDB instead of loading full collections into Python.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Tasks/README_API.md`
- `README.md`
- `tasks/_PLANNING.md`
- `api_utils/mongo_utils/mongo_io.py` — `get_documents` currently returns all matching documents
- `api_utils/services/resource_service.py` — `get_resources` fetches all documents then slices `[offset:offset+size]` in Python (inefficient)
- `tests/mongo_utils/test_mongo_io.py` — integration tests for MongoIO

**Audit note**: `ResourceService` is the only harvested service that paginates today; it does so client-side after a full `get_documents` read. Server-side `skip`/`limit` is the prerequisite for the standardized Get List pattern (R049–R052).

## Goals

- `MongoIO.get_documents(collection_name, match=None, project=None, sort_by=None, skip=None, limit=None)` accepts optional `skip` and `limit` integers.
- When `skip` is provided, apply `.skip(skip)` to the PyMongo cursor; when `limit` is provided, apply `.limit(limit)`.
- Omitting `skip`/`limit` preserves current behavior (return all matching documents).
- Invalid `skip` (`< 0`) or `limit` (`< 1`) raise a clear exception before querying (or document that callers validate via list-query helpers in R049).
- Integration tests cover paginated reads (insert ≥3 documents, assert `skip`/`limit` window).

## Testing Expectations

- `pipenv run db` — start backing database
- `pipenv run test tests/mongo_utils/test_mongo_io.py`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `api_utils/mongo_utils/mongo_io.py` — add `skip`/`limit` to `get_documents`
- `tests/mongo_utils/test_mongo_io.py` — paginated read tests

The agent must not update files outside this list.

## Execution Notes

- Added optional `skip`/`limit` to `MongoIO.get_documents`; validates `skip >= 0` and `limit >= 1`.
- Added integration tests for paginated window and validation errors.
- `pipenv run test`: 158 passed, 6 deselected.
