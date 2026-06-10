# Mentor Hub — shared API utilities

This repo builds and publishes the **`api_utils`** PyPI package (`pip install api-utils`) used across the [Mentor Hub](https://github.com/mentor-forge/mentorhub) system. Packages are published to **AWS CodeArtifact** in the Shared-Services account.

## Prerequisites
- Mentor Hub [Developers Edition](https://github.com/mentor-forge/mentorhub/blob/main/CONTRIBUTING.md)
- Developer [SPA Standard Prerequisites](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/spa_standards.md)
- AWS CLI v2 with SSO profile **`mentorhub-shared`** (Shared-Services, Developer-Packages or SRE)

## Install as a dependency (domain APIs)

After the CodeArtifact migration, domain API developers install a pinned version from CodeArtifact — not git or public PyPI. Public PyPI has an unrelated `api-utils` package; always use the CodeArtifact index.

```bash
mh codeartifact login    # once per session (~12h); included in make update
cd ../mentorhub_coordinator_api
pipenv install
```

Configure the domain API `Pipfile` with a CodeArtifact source and pinned version (see [Dependency Registry Migration](https://github.com/mentor-forge/mentorhub/blob/main/Specifications/DEPENDENCY_MOVE.md)).

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

Libraries use **pinned SemVer** in CodeArtifact (`api-utils==0.2.0`), unlike app containers that publish `:latest` on every merge to `main`. Releasing is two steps — same PR workflow as everything else, plus one command after merge:

```text
PR (feature branch)     merge to main          tag (on main)
─────────────────     ───────────────      ─────────────────
edit pyproject.toml     review + merge       pipenv run tag-release
commit + open PR                             → CI publishes to CodeArtifact
```

### Step 1 — bump version (in your release PR)

Edit `version` in [pyproject.toml](./pyproject.toml) (SemVer), commit with your changes, and merge via PR.

### Step 2 — tag release (after merge, on up-to-date main)

The tag must match `pyproject.toml` (`v0.2.0` ↔ `version = "0.2.0"`). CI enforces this.

```bash
git checkout main && git pull
pipenv run tag-release
```

That creates and pushes `v{version}`; GitHub Actions builds and uploads to CodeArtifact. Requires org variables (`AWS_REGION`, `CODEARTIFACT_*`, `AWS_SHARED_SERVICES_ACCOUNT_ID`) and repo secret `AWS_ROLE_ARN_PUBLISH`.

**Local publish** (SRE / debugging, skips CI): `aws sso login --profile mentorhub-shared` then `pipenv run publish-package`.

## Project Structure

- `api_utils/` - Main package containing:
  - `config/` - Configuration singleton with support for file, environment, and default values
  - `flask_utils/` - Flask-specific utilities (JSON encoder, token, breadcrumb)
  - `mongo_utils/` - MongoDB utilities (MongoIO singleton, document encoding, infinite scroll)
  - `routes/` - Flask route blueprints with factory functions (config, metrics, explorer)

- `tests/` - Test suite for all components

## Domain APIs vs. this library

**Developer Edition:** Domain APIs and this library **validate** JWTs issued by the welcome page / IdP. See [API Standards](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md).

The packaged **demo server** (`api_utils/server.py`) documents config and metrics only; obtain Bearer tokens from your IdP (or the static test token in `tests/e2e_auth.py` for black-box runs).

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
# Get configuration (use a JWT from your IdP, or the token in tests/e2e_auth.py for local E2E)
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