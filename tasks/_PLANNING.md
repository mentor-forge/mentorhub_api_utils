# API Task Automation Framework - Planning

This folder contains coding tasks that an orchestration agent can execute, based on the context and instructions in each task file. This file is a guide for an agent that is helping to plan changes by creating task files to achieve a goal. Create tasks following the [naming conventions](#naming-conventions) and guides below. 

Review **Context** Before creating any task files you should review the following files for context:
- ../mentorhub/DeveloperEdition/standards/api_standards.md
- ./README.md
- ./tasks/_ORCHESTRATE.md
- ./tasks/_PLANNING.md (this file)

## Task File Layout

Each task file must contain the following sections under H1 and H2 headings.

- Under the top H1 task header:
  - Each task file should declare `Status:` **inside the file**, and also encode the status in the **filename prefix** so tasks are visually grouped in the IDE.
  - **Lifecycle statuses (in‑file)**:
    - `Pending`: Not yet started.
    - `Running`: Work is currently being done in the active session.
    - `Blocked`: Waiting on some external dependency or decision.
    - `Shipped`: Implemented, tested, and committed as per the change control process.
    - `Run as needed`: Not part of the main long‑running sequence; to be run manually or opportunistically.
  - **Filename status prefixes (for grouping)**:
    - `AS_NEEDED.` – Tasks that should **not** be part of the main long‑running sequence.
    - `BLOCKED.` – Tasks currently blocked.
    - `PENDING.` – Tasks that are ready to be picked up when their turn comes.
    - `RUNNING.` – (Optional) Tasks currently being executed in this session.
    - `SHIPPED.` – Tasks that are fully implemented and completed.
  - **Type**: `Feature` | `Defect` to describe why we are running this task
  - **Depends On**: `L010_update_profile_openapi` the required predecessor task **in this repo**, or `none` for parallel tasks
  - **Description**: A brief human description of the task.

- Under a **Path anchoring** H2 header:
  - All paths in task files are relative to **this api_utils repository root** (the directory that contains `Pipfile`).
  - Sibling repos must all be sibling folders under a common parent.
  - Standards: `../mentorhub/DeveloperEdition/standards/api_standards.md`
  - In-repo: `README.md`, `docs/openapi.yaml`, `api_utils/...`, `test/...`, `tasks/...`

- Under a **Context** H2 header:
  - A list of context files. This list should always include:
    - `../mentorhub/DeveloperEdition/standards/api_standards.md`
    - `tasks/README_API.md`
    - `README.md`
  - Any other input files for the execution of the task.
  - `AS_NEEDED` tasks may include a **Parameters (edit before running)** subsection here for values to customize before promoting to `Pending`.

- Under a **Goals** H2 header:
  - A list of desired outcomes for the task.
  - Each item should describe the outcome (e.g. "OpenAPI `Profile` schema includes `full_name`").

- Under a **Testing Expectations** H2 header:
  - Can include the creation of new tests for new features.
  - Can include changing existing tests because of modified features.
  - Should always include a description of the tests that should be used to verify completion.
  - In this repo, that typically means some combination of:
    - `pipenv install --dev` — refresh dependencies after `Pipfile` / lockfile changes (CodeArtifact auth; run `mh` first if needed)
    - `pipenv run db` start the backing database (required for all testing)
    = `pipenv run test` — unit tests (pytest, excludes `@pytest.mark.e2e`)
    - `pipenv run dev` — run API dev server locally (for manual or E2E verification)
    - `pipenv run e2e` — end-to-end tests against a running dev server
  - Should always include the **Packaging verification** step:
    - `pipenv run build` — compile Python sources
  - All test files should be identified in **Outputs** (below).

- Under an **Outputs** H2 header:
  - A list of the files that will be created/updated/moved/renamed/etc.
  - `file_name.py` will be updated to support `<Goal>`
  - List all files including new files to be created.
  - The agent will not update files not listed.

- Under an **Execution Notes** H2 header:
  - Reserved for the task execution agent to record plan, commands run, test results, and follow-ups.

## Naming Conventions
- **Recommended filename pattern**:
  - `STATUS.LNNN.short_task_name.md`
  - Examples:
    - `AS_NEEDED.T998.example_update_openapi.md`
    - `PENDING.L010.update_profile_openapi.md`
    - `RUNNING.L020.add_profile_field_tests.md`
    - `SHIPPED.L010.update_profile_openapi.md`

## External repository boundaries

Task planning and execution in **this library repo** (`mentorhub_api_utils`) may read sibling repos for **harvesting** or **documenting downstream adoption**, but orchestration commits only touch this repo.

Allowed external context:

- **`../mentorhub`** — platform standards and shared documentation (e.g. `DeveloperEdition/standards/api_standards.md`).
- **Domain API repos** — read-only reference when harvesting services or drafting downstream follow-on issues (e.g. `../mentorhub_mentee_api`, `../mentorhub_mentor_api`).

Do **not** orchestrate changes in domain API repos from this folder. Record downstream work in § [Downstream follow-on issues](#downstream-follow-on-issues) for humans or those repos' planning agents.

## Standardized Get List pattern

Replace the legacy **infinite-scroll** contract (`after_id`, `limit`, `{items, has_more, next_cursor}`) with **offset/size header pagination** and **query-parameter filters** on list endpoints.

| Layer | Convention |
|-------|------------|
| Pagination headers | `offset` (default `0`), `size` (default `20`, max `100`) |
| Response body | Plain JSON array |
| Text contains | Query param → case-insensitive substring on field (e.g. `?description=onboard`) |
| Enum in-list | Comma-separated query param → MongoDB `$in` (e.g. `?status=active,draft`) |
| Scoped lists | Service supplies base `match` (RBAC, parent id); pagination applies within scope |
| Order by | Query params `sort_by` + `order` (`asc`/`desc`); per-endpoint `order_spec` whitelists fields and defaults |
| MongoDB I/O | `MongoIO.get_documents(..., skip=offset, limit=size)` via `list_query.execute_list_query` |

Implementation tasks: `PENDING.R048` → `PENDING.R049` → (`PENDING.R050`–`PENDING.R052`, `PENDING.R055` in parallel) → `PENDING.R053` → `PENDING.R054`. Route-layer helpers live in `api_utils.flask_utils.list_request`; service/Mongo helpers in `api_utils.mongo_utils.list_query`.

### Services audit (`api_utils/services/`)

| Service | List method today | Pagination | Filters | Action (api_utils) |
|---------|-------------------|------------|---------|-------------------|
| `ResourceService` | `get_resources` | offset/size kwargs; **Python slice after full fetch** | none | R050 — DB pagination + `name`/`description`/`status` filters |
| `PathService` | `get_paths` | none (returns all) | none | R051 — offset/size + optional `name` contains |
| `NoteService` | `get_notes_for_resource` | none (returns all in scope) | none | R052 — offset/size + optional `status` in_list; composites fetch full set |
| `EventService` | — (create only in api_utils) | n/a | n/a | R055 — add `get_events` with `type` in_list + optional `profile_id` scope |
| `JourneyService` | — (`get_my_journey` single doc) | n/a | n/a | no list method |
| `AggregationService` | — (per-resource reads) | n/a | n/a | no generic list; R052 adjusts embedded note fetch |

## Downstream follow-on issues

Paste ISSUE artifacts from `tasks/ISSUE.*.md` into the target repo's planning session (or promote to `PENDING.*` task files there).

### Journey promote + GET detail harvest (R059–R061, `api-utils==0.5.2`)

Harvested from **`mentorhub_mentee_api`** only. Mutation methods return plain Journey; `get_my_journey_detail` embeds read-time `profile`.

| Task | Source | Upstream outcome |
|------|--------|------------------|
| SHIPPED.R059 | `journey_promote_service.py` | `promote_path_to_next`, `promote_module_to_next` |
| SHIPPED.R060 | `journey_detail_service.py` | `get_my_journey_detail`; `"profile"` in `RESTRICTED_UPDATE_FIELDS` |
| SHIPPED.R061 | — | Patch `0.5.2` |

**Not in R059–R061:** `get_journey_progress` (mentor dashboard aggregation) — still local in `mentorhub_mentor_api`; planned in `ISSUE.mentorhub_api_utils.harvest_mentor_services.md`.

**Downstream:**

- **`mentorhub_mentee_api`** — `ISSUE.mentorhub_mentee_api.adopt_journey_harvest_from_api_utils.md`: bump pin, routes → `JourneyService`, **delete entire `src/services/`**.
- **`mentorhub_mentor_api`** — `ISSUE.mentorhub_mentor_api.bump_api_utils_journey_harvest.md`: **interim bump only**; local `journey_service.py` (progress) stays until `harvest_mentor_services` + `adopt_harvested_services`.

## MongoDB dictionary schemas

**Definitive** MongoDB collection/dictionary schema information must come from the **running MongoDB configurator service** (`mentorhub_mongodb_api`), not from files in the `mentorhub_mongodb_api` repository.

Start the backing database if needed (`pipenv run db`), then fetch the latest JSON schema with `curl`:

```bash
curl -X GET "http://localhost:8383/api/configurations/json_schema/<Dictionary>.yaml/latest/" -H "accept: application/json"
```

Replace `<Dictionary>` with the collection name (e.g. `Path`, `Resource`, `Note`). Use this response as the source of truth when updating `docs/openapi.yaml` component schemas or when implementing service projections. Do **not** use deprecated paths under `../mentorhub/Specifications/schemas/`.

If the configurator is unavailable, set the task **Status** to `Blocked` and stop — do not fall back to dictionary YAML files in the `mentorhub_mongodb_api` repo.

## Dependency management

Domain APIs resolve `api-utils` and other packages from **AWS CodeArtifact**. When a task bumps or adds dependencies in `Pipfile` / `Pipfile.lock`, the execution agent must install them with:

```bash
pipenv run install
```

Do **not** use bare `pipenv install` or `pipenv install --dev` in task instructions — those skip the repo’s CodeArtifact auth wrapper (`scripts/pipenv-install.sh`). Run `mh` once per shell session before `pipenv run install` if CodeArtifact credentials are not already available (see `README.md` and `../mentorhub/DeveloperEdition/standards/api_standards.md`).

Task **Testing Expectations** and **Goals** should call out `pipenv run install` whenever `Pipfile` or `Pipfile.lock` changes.

## MongoDB access

Service code must route all MongoDB I/O through **`MongoIO`** (`api_utils.mongo_utils.mongo_io`) — use `get_document`, `get_documents`, `create_document`, `update_document`, and `upsert_document` as appropriate. Do **not** call PyMongo directly (for example `mongo.get_collection(...)` followed by `collection.find`, `find_one`, `insert_one`, or similar).

When planning or reviewing tasks, include this rule in **Context** or **Goals** for any work that touches `src/services/`. If a task cannot comply without an upstream `api_utils` change, document the gap and any temporary exception in that task’s **Execution Notes** — not here.

Reference: `../mentorhub_api_utils/api_utils/mongo_utils/mongo_io.py`, `../mentorhub/DeveloperEdition/standards/api_standards.md`, and shipped task `SHIPPED.L070.refactor_services_to_mongoio.md`.

## Sample task file

For a complete example of a well‑formed `Run as needed` task, see:

- `AS_NEEDED.T998.example_update_openapi.md`
