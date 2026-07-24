# Mentor Hub — shared API utilities

This repo builds and publishes the **`api_utils`** PyPI package (`pip install api-utils`) used across the [Mentor Hub](https://github.com/mentor-forge/mentorhub) system. Packages are published to **AWS CodeArtifact** in the Shared-Services account.

## Current State

Mentor Hub is **pre-MVP**. There is **no production environment yet**. Nothing here
is running in production, so there is no live user data to migrate and breaking
changes carry no production risk until MVP. Collection schemas are likewise
unversioned for release purposes — every collection is at `0.1.0.0` and will not be
formally versioned until we cut MVP.

## Prerequisites
- Mentor Hub [Developers Edition](https://github.com/mentor-forge/mentorhub/blob/main/CONTRIBUTING.md)
- Developer [SPA Standard Prerequisites](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/spa_standards.md)

## Install as a dependency (domain APIs)

```bash
mh              # once per session (~12h)
pipenv install
```

## Developer Commands

```bash
## Install dependencies
pipenv install --dev

# start backing db container (required for MongoIO unit/integration tests)
pipenv run db

## run unit tests (includes MongoIO Integration Tests)
pipenv run test

## run demo dev server - captures command line, serves API at localhost:9092
## Note: dev uses a fixed JWT_SECRET for local E2E; see tests/e2e_auth.py
pipenv run dev

## run E2E tests (assumes running API at localhost:9092)
pipenv run e2e

## build package for deployment
pipenv run build

## release: tag after merge — see Release and publish
pipenv run tag-release

## publish to CodeArtifact locally (SRE / publish role; after SSO login)
pipenv run publish-package

## format code
pipenv run format

## lint code
pipenv run lint
```

## Release and publish

Libraries use **pinned SemVer** in CodeArtifact (`api-utils==0.6.0`). Releasing is two steps:
- Work on a feature branch, make sure to bump version in pyproject.toml before opening PR.
- After PR is approved and merged, use ``pipenv run tag-release`` to publish the new code

**Local publish** (SRE / debugging, skips CI): `aws sso login --profile mentorhub-shared` then `pipenv run publish-package`.

## Project Structure

- `api_utils/` - Main package containing:
  - `config/` - Configuration singleton with support for file, environment, and default values
  - `flask_utils/` - Flask-specific utilities (`MongoJSONEncoder` outbound id/date → string, token, breadcrumb)
  - `mongo_utils/` - MongoDB utilities (MongoIO singleton, `encode_document` inbound string → ObjectId/datetime, list query, legacy infinite scroll)
  - `services/` - Shared domain service classes (Note, Event, Resource, Path, Journey, Aggregation, Plan, Mentee, Encounter, Profile)
  - `routes/` - Flask route blueprints with factory functions (config, metrics, explorer)

- `tests/` - Test suite for all components

### Shared domain services

Domain APIs import service classes from `api_utils.services` (or top-level `api_utils`) rather than maintaining duplicate `src/services/` copies:

```python
from api_utils.services import JourneyService, PathService
# or
from api_utils import JourneyService, PathService
```

The full shared surface is: `AggregationService`, `EncounterService`,
`EventService`, `JourneyService`, `MenteeService`, `NoteService`, `PathService`,
`PlanService`, `ProfileService`, and `ResourceService`.

### MongoDB ObjectId handling (inbound vs outbound)

MongoDB document `_id`s (and other id/date fields) are BSON types in the
database but plain strings on the HTTP wire. Two utilities own that conversion,
and **service code should rely on them rather than hand-rolling `ObjectId(...)`
or `str(...)` conversions**:

- **Inbound — `api_utils.mongo_utils.encode_document`** (write / query side):
  Ids arriving from clients are handled as **strings** all the way through the
  service, and are encoded to BSON `ObjectId` (and ISO strings to `datetime`)
  **at the last moment, immediately before the `MongoIO` call**. Name the id and
  date fields explicitly:

  ```python
  from api_utils.mongo_utils import encode_document

  encode_document(document, ["_id", "profile_id"], ["completed"])
  MongoIO.get_instance().create_document(collection, document)
  ```

  This matters for **match filters** too: `MongoIO.get_documents(match=...)` does
  **not** coerce match values (unlike `get_document` / `update_document`, which
  wrap `document_id` in `ObjectId(...)`). An unencoded string id in a `match`
  silently matches nothing against a stored `ObjectId`, so encode the id in the
  filter first.

- **Outbound — `api_utils.flask_utils.ejson_encoder.MongoJSONEncoder`**
  (read / response side): documents read from Mongo keep their `ObjectId` /
  `datetime` values **unchanged** as they flow back through services and routes.
  They are decoded to strings **only at the final step**, when Flask serializes
  the HTTP reply. The encoder is registered app-wide (`app.json =
  MongoJSONEncoder(app)` in `server.py`), so route/service code should **not**
  pre-stringify ids for output.

In short: **strings in, encode at the `MongoIO` boundary; `ObjectId` out, decode
at the Flask serialization boundary.**

### Standardized Get List pattern

List endpoints use **offset/size request headers** (defaults `0` / `20`, max `100`), a plain JSON **array** response body, **query-parameter filters** (`contains`, `in_list`), and **order-by** query params (`sort_by`, `order`) validated per-endpoint via `order_spec`.

```python
from api_utils.flask_utils.list_request import parse_list_request
from api_utils.services.resource_service import (
    ResourceService,
    RESOURCE_LIST_FILTERS,
    RESOURCE_LIST_ORDER,
)

offset, size, filters, sort_by = parse_list_request(
    request, RESOURCE_LIST_FILTERS, RESOURCE_LIST_ORDER
)
items = ResourceService.get_resources(token, breadcrumb, offset, size, filters, sort_by)
```

Legacy `execute_infinite_scroll_query` is **deprecated** — migrate domain APIs to `list_query.execute_list_query`.

## Domain APIs vs. this library

**Developer Edition:** Domain APIs and this library **validate** Bearer JWTs only; they do not mint credentials. Journey SPAs obtain tokens from the umbrella **developer sign-in page** ([`login.html`](https://github.com/mentor-forge/mentorhub/blob/main/login.html) at `http://127.0.0.1:8080/login.html`), which mints persona JWTs in the browser (`iss: dev-idp`, `aud: dev-api`, shared `JWT_SECRET`). See [API Standards](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md).

The packaged **demo server** (`api_utils/server.py`) is separate from that SPA login flow—it exposes config, metrics, and docs for library testing. For local E2E against `pipenv run dev`, use the static token in `tests/e2e_auth.py` (same `JWT_SECRET` as Developer Edition compose).

## Demo Server

A demonstration server is included to showcase the utilities and support black-box testing.
See [server.py](./api_utils/server.py) for sample implementation details.

### Starting the Server

```bash
# Start the demo server (JWT_SECRET matches tests/e2e_auth.py)
pipenv run dev

# Server will be available at http://localhost:9092
```

### API Explorer

Visit **http://localhost:9092/docs/explorer.html** for an interactive API explorer with:
- Complete endpoint documentation
- Try-it-out functionality for testing
- Request/response examples
- Authentication testing

### Available Endpoints

- `/docs/explorer.html` - Interactive API Explorer (Swagger UI)
- `/docs/openapi.yaml` - OpenAPI specification
- `/api/config` - Configuration endpoint (requires valid JWT token)
- `/metrics` - Prometheus metrics endpoint

### Quick curl Examples

```bash
# Get configuration (Developer Edition: sign in at login.html and copy access_token from the SPA;
# for pipenv run dev E2E, use tests/e2e_auth.py)
curl http://localhost:9092/api/config \
  -H "Authorization: Bearer $TOKEN"

# Get Prometheus metrics
curl http://localhost:9092/metrics
```

### What the Server Demonstrates

- Config singleton initialization
- MongoIO singleton connection
- Flask route registration with factory pattern
- Prometheus metrics integration
- JWT token authentication and authorization
- Interactive API documentation
- Graceful shutdown handling