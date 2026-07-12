# Mentor Hub — shared API utilities

This repo builds and publishes the **`api_utils`** PyPI package (`pip install api-utils`) used across the [Mentor Hub](https://github.com/mentor-forge/mentorhub) system. Packages are published to **AWS CodeArtifact** in the Shared-Services account.

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

Libraries use **pinned SemVer** in CodeArtifact (`api-utils==0.5.0`). Releasing is two steps:
- Work on a feature branch, make sure to bump version in pyproject.toml before opening PR.
- After PR is approved and merged, use ``pipenv run tag-release`` to publish the new code

**Local publish** (SRE / debugging, skips CI): `aws sso login --profile mentorhub-shared` then `pipenv run publish-package`.

## Project Structure

- `api_utils/` - Main package containing:
  - `config/` - Configuration singleton with support for file, environment, and default values
  - `flask_utils/` - Flask-specific utilities (JSON encoder, token, breadcrumb)
  - `mongo_utils/` - MongoDB utilities (MongoIO singleton, document encoding, list query, legacy infinite scroll)
  - `services/` - Shared domain service classes (Note, Event, Resource, Path, Journey, Aggregation)
  - `routes/` - Flask route blueprints with factory functions (config, metrics, explorer)

- `tests/` - Test suite for all components

### Shared domain services

Domain APIs import service classes from `api_utils.services` (or top-level `api_utils`) rather than maintaining duplicate `src/services/` copies:

```python
from api_utils.services import JourneyService, PathService
# or
from api_utils import JourneyService, PathService
```

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