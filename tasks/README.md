# Mentor Hub — Mentor API

## Prerequisites
- Mentor Hub [Developers Edition](https://github.com/mentor-forge/mentorhub/blob/main/CONTRIBUTING.md)
- Developer [API Standard Prerequisites](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md)

## Developer Commands

```bash
## Install dependencies (run `mh` first for CodeArtifact auth)
pipenv run install

## Start backing database
## Note: stop existing containers if needed before starting local services
pipenv run db

## Run unit tests
pipenv run test

## Run API server in dev mode
## Serves API at localhost:8391 and supports local development flow
pipenv run dev

## Run E2E tests (assumes running API at localhost:8391)
## E2E does NOT require containerized or packaged deployment.
## It runs against a locally running API + DB-backed environment.
pipenv run e2e

## Run tests with coverage report
pipenv run coverage

## Build application (pre-compiles Python code)
pipenv run build

## Run backing database and API services
pipenv run api

## Format code
pipenv run format

## Lint code
pipenv run lint

## Project Structure

- `src/` - Main package containing:
  - `server.py` - API entrypoint
  - `routes/` - HTTP request/response handlers
  - `services/` - Business logic and RBAC

- `test/` - Test suite with matching directory structure:
  - `routes/` - Route unit tests
  - `services/` - Service unit tests
  - `e2e/` - End-to-end tests flagged with `@pytest.mark.e2e`

## API Endpoints

see the [Open API Specifications](./docs/openapi.yaml) for details on the API

For E2E, mint a Bearer token via `test/e2e/e2e_auth.py` (`get_auth_token()`) with `pipenv run dev` (matching `JWT_SECRET`).

### Simple Curl Commands:
```bash
# Bearer token for local dev (same JWT settings as pipenv run dev / e2e):
export TOKEN="$(PYTHONPATH=. pipenv run python -c 'from test.e2e.e2e_auth import get_auth_token; print(get_auth_token())')"

# Get the API Configuration
curl http://localhost:8391/api/config \
  -H "Authorization: Bearer $TOKEN"

```