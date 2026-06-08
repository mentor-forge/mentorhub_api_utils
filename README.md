# Mentor Hub — shared API utilities

This repo builds and publishes the **`mentorhub_api_utils`** PyPI library used across the [Mentor Hub](https://github.com/mentor-hub-system/mentorhub) system.

## ⚠️ Security Requirements

**CRITICAL:** `JWT_SECRET` must be explicitly set before using api_utils in any environment. The application will fail to start if `JWT_SECRET` is not configured.

```bash
# For development/testing
export JWT_SECRET='your-development-secret'

# For production (use strong, randomly generated secret)
export JWT_SECRET=$(openssl rand -base64 32)
```

**Never use the default JWT_SECRET value in any environment.** See [SECURITY.md](./SECURITY.md) for complete security guidance.

## Prerequisites
- Python [v3.14](https://www.python.org/downloads/)
- pipenv [v2026.0.3](https://pipenv.pypa.io/en/latest/installation.html) or newer 
- [MongoDB Compass](https://www.mongodb.com/docs/compass/install/?operating-system=linux&package-type=.deb) (optional - connection string is localhost://mongodb:27017)

## Developer Commands

```bash
## Install dependencies
pipenv install --dev

# start backing db container (required for MongoIO unit/integration tests)
pipenv run db

## run unit tests (includes MongoIO Integration Tests)
pipenv run test

## run demo dev server - captures command line, serves API at localhost:8385
## Note: dev uses a fixed JWT_SECRET for local E2E; see tests/e2e_auth.py
pipenv run dev

## run E2E tests (assumes running API at localhost:8385)
pipenv run e2e

## build package for deployment
pipenv run build

## format code
pipenv run format

## lint code
pipenv run lint
```

## Project Structure

- `api_utils/` - Main package containing:
  - `config/` - Configuration singleton with support for file, environment, and default values
  - `flask_utils/` - Flask-specific utilities (JSON encoder, token, breadcrumb)
  - `mongo_utils/` - MongoDB utilities (MongoIO singleton, document encoding, infinite scroll)
  - `routes/` - Flask route blueprints with factory functions (config, metrics, explorer)

- `tests/` - Test suite for all components

## Domain APIs vs. this library

**Developer Edition:** Domain APIs and this library **validate** JWTs issued by the welcome page / IdP; they do not expose HTTP endpoints that mint credentials. See [API Standards](https://github.com/mentor-hub-system/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md).

The packaged **demo server** (`api_utils/server.py`) documents config and metrics only; obtain Bearer tokens from your IdP (or the static test token in `tests/e2e_auth.py` for black-box runs).

## Demo Server

A demonstration server is included to showcase the utilities and support black-box testing.
See [server.py](./api_utils/server.py) for sample implementation details.

### Starting the Server

```bash
# Start the demo server (JWT_SECRET matches tests/e2e_auth.py)
pipenv run dev

# Server will be available at http://localhost:8385
```

### API Explorer

Visit **http://localhost:8385/docs/explorer.html** for an interactive API explorer with:
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
curl http://localhost:8385/api/config \
  -H "Authorization: Bearer $TOKEN"

# Get Prometheus metrics
curl http://localhost:8385/metrics
```

### What the Server Demonstrates

- Config singleton initialization
- MongoIO singleton connection
- Flask route registration with factory pattern
- Prometheus metrics integration
- JWT token authentication and authorization
- Interactive API documentation
- Graceful shutdown handling

## Package Installation

**Installation from GitHub (HTTPS with Token):**

All installations use HTTPS with GitHub Personal Access Tokens (PATs).

**Normal Installation:**
```bash
# Configure git to use your GitHub token (one-time setup):
git config --global url."https://<YOUR_TOKEN>@github.com/".insteadOf "https://github.com/"

# Then install normally
pipenv install git+https://github.com/mentor-hub-system/api_utils.git
```

**Development Installation (Editable Mode):**
```bash
pipenv install -e git+https://github.com/mentor-hub-system/api_utils.git#egg=api-utils
```

Use editable mode when you're **simultaneously working on both**:
- The consuming project (e.g., evaluator_api)
- AND the `api_utils` package itself

Editable mode links to your local `api_utils` clone, so changes to `api_utils` are immediately available in the consuming project without reinstalling.

## Security

api_utils implements security best practices including:
- **JWT signature verification** - Tokens are validated with proper signature verification when `JWT_SECRET` is configured
- **Fail-fast validation** - Application will not start if `JWT_SECRET` uses the default insecure value
- **Secret masking** - Configuration secrets are masked in logs and API responses
### Production Security Checklist

Before deploying to production, ensure:
- [ ] `JWT_SECRET` is set to a strong, randomly generated value
- [ ] MongoDB connection uses authentication and encryption
- [ ] HTTPS/TLS is configured
- [ ] Monitoring and logging are enabled

**See [SECURITY.md](./SECURITY.md) for complete security documentation.**

# Future Roadmap

api_utils is the official standards-compliant Python package used by all Mentor Hub python projects. It is currently installed via HTTPS with GitHub Personal Access Tokens (PATs). 
Once a number of production deployed consumers exist, version stability becomes important so they can pin known-good releases instead of tracking a moving branch. We will introduce semantic versioning via Git tags and expose the version in the package, allowing consumers to pin exact versions.
Once funding or organizational maturity allows, infrastructure improvements can replace the Git-based distribution without changing the package itself.
	•	Stand up a private JFrog Artifactory PyPI repository, providing centralized, permissioned package hosting.
	•	Migrate consumers from git+https installs to the private PyPI index by changing only index configuration, preserving package names and versions.
	•	Enable artifact promotion, vulnerability scanning, and access controls (e.g., Xray, repo permissions).