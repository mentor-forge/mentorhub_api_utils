# R086 – E2E tests for demo-server consume GETs

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R085_register_get_routes_on_sample_server`  
**Description**: Black-box tests against `pipenv run dev` for every shared GET mounted on the demo server: auth, JSON array lists with offset/size, get-by-id 404.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — E2E token via `tests/e2e_auth.py`; port `COMMON_CODE_API_PORT` (8385)
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tests/test_server.py` — existing e2e style (`@pytest.mark.e2e`, lazy `requests`, `BASE_URL`)
- `tests/e2e_auth.py` — admin persona JWT (`adam`)
- `api_utils/server.py` — prefixes from R085
- `Pipfile` — `e2e`, `dev`, `db` scripts

Demo server already initializes MongoIO at import. Lists against an empty or seeded Developer Edition DB are valid: `200` + `[]` is success. Do not fail if seed data is absent. Do not assert specific document fields unless the test inserts via a **global POST that already exists on a service** — prefer not to add POST routes in this task; stay GET-only.

### Cases (each list prefix)

For `/api/resource`, `/api/path`, `/api/plan`, `/api/profile`, `/api/notification`, `/api/event`:

- No `Authorization` → `401`
- Valid Bearer → `200` and `isinstance(body, list)`
- Headers `offset: 0`, `size: 1` → `200`, `len(body) <= 1`
- Get-by-id of a random 24-hex id (Resource/Path/Plan/Profile only) → `404`

For `/api/note` and `/api/encounter` list GETs:

- Missing required query (`resource_id` / `mentee_id`) → `400`
- With a well-formed ObjectId query + token → `200` and `isinstance(body, list)` (empty OK)

For item-only prefixes (`/api/journey/<id>`, `/api/mentee/<id>`, `/api/aggregation/<id>`, `/api/external-event/<id>`):

- No token → `401`
- Unknown id + token → `404` (ExternalEvent non-admin would also 404; e2e token is **admin** so unknown id is still 404)

Do not assert `X-Pagination-*` or cursor keys. Fail the test if the list body is a dict with `items` / `has_more` / `next_cursor`.

Put new tests in `tests/test_get_routes_e2e.py` (or `tests/e2e/test_get_routes.py` if you add that package) with `@pytest.mark.e2e` so `pipenv run test` continues to deselect them.

## Goals

- E2E module covers every mounted GET prefix as above.
- `pipenv run test` still deselects e2e (existing 23-ish deselected may grow).
- `pipenv run e2e` green against a running demo server + MongoDB.

## Testing Expectations

From repo root (server and DB must be up for e2e):

- `pipenv run db` — if Mongo is not already running
- `pipenv run test` — unit suite; new e2e tests deselected
- Start demo server: `pipenv run dev` (already sets `JWT_SECRET` / `PYTHONPATH`)
- `pipenv run e2e`
- `pipenv run lint` — R086 files `black`-clean
- `pipenv run build`

If e2e cannot run because Mongo/configurator is down, set **Status** to `Blocked` and stop — do not skip the e2e file or mark tests xfail.

## Outputs

- `tests/test_get_routes_e2e.py` — new (or `tests/e2e/test_get_routes.py` plus `__init__.py` if splitting)

The agent must not update files outside this list.

## Execution Notes

**Approach**: Added `tests/test_get_routes_e2e.py` with parametrized `@pytest.mark.e2e` tests mirroring `tests/test_server.py` (lazy `requests`, `BASE_URL`, `get_auth_token`). Covers all six list prefixes (401, 200 array, size header), four get-by-id 404 prefixes, note/encounter query validation, and item-only auth/not-found paths.

**Aggregation deviation**: `GET /api/aggregation/<resource_id>` for an unknown resource returns `200` + `null` per R082 outbound visibility (not HTTP 404). Dedicated test `test_aggregation_unknown_resource_id_returns_null` documents that contract; journey/mentee/external-event still assert 404.

**Test results** (demo server on 8385, Mongo on 8383):

- `pipenv run test`: 237 passed, 57 deselected
- `pipenv run e2e`: 40 passed, 254 deselected
- `black --check tests/test_get_routes_e2e.py`: clean
- `pipenv run build`: success
