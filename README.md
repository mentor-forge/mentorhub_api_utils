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

# start backing db container (required for integration and e2e tests)
pipenv run db

## run unit tests (pure/mocked, no backing services)
pipenv run test

## run integration tests (exercise services + MongoIO against the DB; run `pipenv run db` first)
pipenv run integration

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

Libraries use **pinned SemVer** in CodeArtifact (`api-utils==1.0.0`). Releasing is two steps:
- Work on a feature branch, make sure to bump version in pyproject.toml before opening PR.
- After PR is approved and merged, use ``pipenv run tag-release`` to publish the new code

**Local publish** (SRE / debugging, skips CI): `aws sso login --profile mentorhub-shared` then `pipenv run publish-package`.

## Project Structure

- `api_utils/` - Main package containing:
  - `config/` - Configuration singleton with support for file, environment, and default values
  - `flask_utils/` - Flask-specific utilities (`MongoJSONEncoder` outbound id/date → string, token, breadcrumb)
  - `mongo_utils/` - MongoDB utilities (MongoIO singleton, `encode_document` inbound string → ObjectId/datetime, list query)
  - `services/` - Shared domain service classes (Note, Event, Resource, Path, Journey, Aggregation, Plan, Mentee, Encounter, Profile, ExternalEvent, Notification)
  - `routes/` - Flask route blueprints with factory functions (config, metrics, explorer, shared GET routes)

- `tests/` - Test suite for all components

### Shared domain services

Domain APIs import service classes from `api_utils.services` (or top-level `api_utils`) rather than maintaining duplicate `src/services/` copies:

```python
from api_utils.services import JourneyService, PathService
# or
from api_utils import JourneyService, PathService
```

The full shared surface is: `AggregationService`, `EncounterService`,
`EventService`, `ExternalEventService`, `JourneyService`, `MenteeService`,
`NoteService`, `NotificationService`, `PathService`, `PlanService`,
`ProfileService`, and `ResourceService`.

#### Data-boundary contract

One service domain **controls** a collection; any domain may **consume**
(GET) or **create** immutable documents.

**Shared services** (this package) own:

- **Outbound** GET / list — every shared GET and list applies outbound
  filters from the caller token: admin is unrestricted; non-admin callers
  are scoped by token `profile_id` / `customer_id` / `mentor_id` and
  `status != archived`. Get-by-id uses the same filter after fetch (404
  when the document is hidden, so ids are not leaked via 403). Helpers live
  in `api_utils.services.rbac` (`build_outbound_match`, `require_outbound`,
  …).
- **Global POST** — any journey domain may create immutable documents via
  `EventService.create_event`, `NotificationService.create_notification`,
  and `ProfileService.create_profile`.

**Domain API subclasses** extend the shared class and own enrich, control
POST, PATCH / PUT, and mutate for collections they **control**, plus
**inbound** who-may-write checks (who may PATCH or mutate — separate from
outbound visibility). Methods are `@classmethod` so subclass overrides
dispatch. **Routes import the local subclass**, not `api_utils.services`
directly.

```python
# src/services/journey_service.py
from api_utils.services import JourneyService as SharedJourneyService

class JourneyService(SharedJourneyService):
    @classmethod
    def _check_permission(cls, token, operation, journey_id=None):
        ...  # inbound: who may PATCH / mutate (not outbound)

    @classmethod
    def update_journey(cls, journey_id, data, token, breadcrumb):
        cls._check_permission(token, "update", journey_id=journey_id)
        ...

# src/routes/journey_routes.py
from src.services.journey_service import JourneyService
```

#### Shared GET route factories

`api_utils.routes.shared_get_routes` provides `create_*_get_routes(service_cls)`
factories that return a Flask Blueprint wired for shared consume GETs. Pass the
**local service subclass** (not `api_utils.services` directly). Include the
factory blueprint, then add control POST/PATCH routes on the same blueprint:

```python
from api_utils.routes.shared_get_routes import create_resource_get_routes
from src.services.resource_service import ResourceService

def create_resource_routes():
    bp = create_resource_get_routes(ResourceService)
    @bp.route("", methods=["POST"])
    def create_resource():
        ...
    return bp
```

All twelve factories are exported from `api_utils` (e.g.
`create_resource_get_routes`, `create_path_get_routes`, …). See
`tasks/SHIPPED.R084.shared_get_route_factories.md` for the full factory table
and URL shapes.

**List GET** responses are a plain JSON **array** of documents. Pagination uses
request headers **`offset`** and **`size`** only (defaults `0` / `20`, max
`100`). There is **no** cursor envelope and **no** `X-Pagination-*` response
headers in api_utils.

**Get-by-id GET** returns the document JSON (or **404** when missing or hidden
by outbound RBAC).

#### Downstream planning artifacts

Domain API repos should pin **`api-utils==1.0.0`** and follow the issue
artifacts in this repo's `tasks/` folder (not orchestrated from here):

- [`tasks/ISSUE.journey_api.md`](tasks/ISSUE.journey_api.md) — Journey
  control POST/PATCH/mutate on the Mentee API subclass
- [`tasks/ISSUE.mentorhub_admin_api.profile_create.md`](tasks/ISSUE.mentorhub_admin_api.profile_create.md)
- [`tasks/ISSUE.mentorhub_customer_api.profile_control.md`](tasks/ISSUE.mentorhub_customer_api.profile_control.md)
- [`tasks/ISSUE.mentorhub_discovery_api.notification_control.md`](tasks/ISSUE.mentorhub_discovery_api.notification_control.md)
- [`tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md`](tasks/ISSUE.mentorhub_mentor_api.extend_shared_services.md)
- [`tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md`](tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md)

Collection names, roles, and event types are inline `Config` constants
(`PROFILE_COLLECTION_NAME`, `ROLE_ADMIN`, `EVENT_TYPE_LOGIN`, …) assigned at
construction — not loaded from `config_strings` or overwritten by
`initialize()`. Identity, Login, Card, Dashboard, and Subscription collection
keys were dropped; ExternalEvent, Notification, Setting, Payment, and the
Discovery `EVENT_TYPE_*` values are included.

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

List endpoints use **offset/size request headers** (defaults `0` / `20`, max
`100`), a plain JSON **array** response body, **query-parameter filters**
(`contains`, `in_list`), and **order-by** query params (`sort_by`, `order`)
validated per-endpoint via `order_spec`. Domain APIs should prefer the shared
GET route factories (see **Shared GET route factories** above) rather than
copy-pasting list handlers.

The factories call `parse_list_request` internally. When adding a custom list
route, use the same helper:

```python
from api_utils.flask_utils.list_request import parse_list_request
from src.services.resource_service import ResourceService, RESOURCE_LIST_FILTERS, RESOURCE_LIST_ORDER

offset, size, filters, sort_by = parse_list_request(
    request, RESOURCE_LIST_FILTERS, RESOURCE_LIST_ORDER
)
items = ResourceService.get_resources(token, breadcrumb, offset, size, filters, sort_by)
```

## Domain APIs vs. this library

**Developer Edition:** Domain APIs and this library **validate** Bearer JWTs only; they do not mint credentials. Journey SPAs obtain tokens from the umbrella **developer sign-in page** ([`login.html`](https://github.com/mentor-forge/mentorhub/blob/main/login.html) at `http://127.0.0.1:8080/login.html`), which mints persona JWTs in the browser (`iss: dev-idp`, `aud: dev-api`, shared `JWT_SECRET`). See [API Standards](https://github.com/mentor-forge/mentorhub/blob/main/DeveloperEdition/standards/api_standards.md).

The packaged **demo server** (`api_utils/server.py`) is separate from that SPA
login flow—it exposes config, metrics, docs, and every shared GET factory for
library testing. The demo server mounts `create_*_get_routes` with the **shared**
`api_utils.services` classes (no domain subclass). For local E2E against
`pipenv run dev`, use the static token in `tests/e2e_auth.py` (same
`JWT_SECRET` as Developer Edition compose).

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
- Shared GET routes (Bearer JWT; list = JSON array, `offset`/`size` headers):
  - `/api/resource`, `/api/path`, `/api/plan`, `/api/profile`
  - `/api/notification`, `/api/event`, `/api/note`, `/api/journey`
  - `/api/encounter`, `/api/mentee`, `/api/aggregation`, `/api/external-event`

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