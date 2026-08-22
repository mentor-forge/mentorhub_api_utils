# R083 – Flatten shared Resource GET-by-id to a plain document

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R082_apply_outbound_rbac_to_shared_gets`  
**Description**: Shared consume GETs return a JSON **array** (lists) or a **plain document** (get-by-id). Strip the leftover Resource BFF composite so `get_resource` matches Path/Plan. Confirm api_utils has no cursor or extra pagination-header contract.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Standards: `../mentorhub/DeveloperEdition/standards/api_standards.md`
- In-repo: `README.md`, `api_utils/services/`, `tests/services/`, `tasks/`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — **Standardized Get List pattern**
- `tasks/_PLANNING.md` — **Standardized Get List pattern**
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R074.audit_and_remove_infinite_scroll.md`
- `tasks/SHIPPED.R079.strip_remaining_control_mutations.md`
- `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md`
- `api_utils/services/resource_service.py` — `get_resource` still returns `{resource, aggregation, notes}`
- `api_utils/services/note_service.py` — `list_all_notes_for_resource` (MAX_SIZE helper for composites)
- `tests/services/test_resource_service.py`

Infinite-scroll (`after_id`, `{items, has_more, next_cursor}`) was removed in R074. Do **not** add `X-Pagination-*` response headers (mentor API invented those locally). List responses are a bare JSON array; request pagination is `offset`/`size` headers only.

### Why this task is first

R084 will expose `GET /api/resource/<id>` via `create_resource_get_routes`. That route must serialize whatever `service_cls.get_resource` returns. A `{resource, aggregation, notes}` payload is Mentee BFF enrich, not shared consume.

## Goals

- `ResourceService.get_resource` returns the **raw Resource document** after outbound `require_outbound` (404 if missing or hidden). No nested aggregation or notes.
- Capture the removed composite body (classmethod/`cls` form) in `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md` under a **Harvest-back: Resource GET composite** heading if it is not already there. Mentee subclass `get_resource` may call `super().get_resource` then attach aggregation/notes.
- Unit tests for `get_resource` assert a document with Resource fields, not a `{resource, aggregation, notes}` envelope.
- Repo-wide audit of `api_utils/` and `tests/` (not `tasks/`): zero `after_id`, `has_more`, `next_cursor`, `X-Pagination-`. `list_all_notes_for_resource` may remain as a service helper (it is offset/size with `MAX_SIZE`, not a cursor API) but must **not** become an HTTP route in later tasks.
- No version bump (still unpublished `1.0.0`).

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `PYTHONPATH=. pipenv run pytest tests/services/test_resource_service.py` (Pipfile `test` script ignores extra paths)
- `pipenv run test`
- `pipenv run lint` — R083 files `black`-clean; do not churn unrelated pre-existing lint
- `pipenv run build`

## Outputs

- `api_utils/services/resource_service.py`
- `tests/services/test_resource_service.py`
- `tasks/ISSUE.mentorhub_mentee_api.extend_shared_services.md` — append Resource composite harvest-back if missing

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
