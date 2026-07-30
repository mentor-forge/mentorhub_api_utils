# R074 – Audit downstream APIs and remove infinite scroll from api_utils

**Status**: Pending  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Confirm no domain API still imports `execute_infinite_scroll_query` or exposes cursor list contracts (`after_id`, `has_more`, `next_cursor`). Record ISSUE artifacts for any stragglers, then delete the deprecated `infinite_scroll` module and its public export from api_utils.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `README.md` — deprecated infinite-scroll note
- `tasks/_PLANNING.md` — **Standardized Get List pattern**, **External repository boundaries**
- `tasks/_ORCHESTRATE.md`
- `tasks/SHIPPED.R049.add_list_query_utilities.md` — replacement (`list_query.execute_list_query`)
- `tasks/SHIPPED.R053.deprecate_infinite_scroll.md` — deprecation window
- `api_utils/mongo_utils/infinite_scroll.py`
- `api_utils/mongo_utils/__init__.py`
- `tests/mongo_utils/test_infinite_scroll.py`

### Downstream API repos to audit (read-only)

Search each sibling repo's Python tree for:

| Pattern | Meaning |
| --- | --- |
| `execute_infinite_scroll_query` | Direct api_utils import |
| `from api_utils.mongo_utils import ... infinite` | Re-export import |
| `after_id` | Cursor query param in routes/services |
| `has_more`, `next_cursor` | Cursor response envelope |

Repos (audit all that exist under the common parent):

- `../mentorhub_mentee_api`
- `../mentorhub_mentor_api`
- `../mentorhub_customer_api`
- `../mentorhub_runbook_api`
- `../mentorhub_coordinator_api`
- `../mentorhub_admin_api` (if present)
- `../mentorhub_discovery_api` (if present)

At planning time **mentee** and **mentor** APIs have migrated; **customer_api** still uses `execute_infinite_scroll_query` in multiple local services — expect an ISSUE artifact there before removal can ship.

### Removal scope (api_utils only)

Delete the deprecated parallel pagination path:

- `api_utils/mongo_utils/infinite_scroll.py` — raw PyMongo `collection.find()` cursor helper (bypasses `MongoIO`)
- `tests/mongo_utils/test_infinite_scroll.py`
- Public export from `api_utils/mongo_utils/__init__.py` and `__all__`
- README references to `execute_infinite_scroll_query`

**Do not** remove `MongoIO.get_collection` — it remains for internal MongoIO I/O. The deprecated complexity is the **second list-pagination code path** that required services to pass raw collections into `execute_infinite_scroll_query` instead of `MongoIO.get_documents` + `list_query`.

### Gate

**Removal sub-goals apply only when the audit finds zero hits** for `execute_infinite_scroll_query` across all domain API repos. If any repo still imports it:

1. Complete the audit and write findings to **Execution Notes**.
2. Create `tasks/ISSUE.<repo>.migrate_off_infinite_scroll.md` (paste-ready for that repo's planning agent).
3. Set task **Status** to `Blocked` and **do not** delete `infinite_scroll.py` or bump version.

Promote back to **Pending** when downstream migration ISSUEs are shipped and audit re-run is clean.

## Goals

- Audit matrix in **Execution Notes** listing each domain API repo and pass/fail for infinite-scroll usage.
- `ISSUE.*.md` created for every repo still on cursor pagination (expected: `mentorhub_customer_api`).
- When audit is clean: remove `infinite_scroll` module, tests, and public exports; README points only to Get List pattern.
- When audit is clean: bump `pyproject.toml` **patch** version (breaking removal of exported symbol).

## Testing Expectations

When removal proceeds:

- `pipenv run test` — no remaining imports of `infinite_scroll`
- `pipenv run lint`
- `pipenv run build`

When blocked at audit gate, no code changes beyond ISSUE task files.

## Outputs

Always (audit phase):

- `tasks/ISSUE.*.md` — one per repo with remaining usage (create as needed)
- This task file — **Execution Notes** with audit matrix; **Status** updated to `Blocked` or left `Pending`/`Shipped`

When audit is clean (removal phase):

- `api_utils/mongo_utils/infinite_scroll.py` — delete
- `tests/mongo_utils/test_infinite_scroll.py` — delete
- `api_utils/mongo_utils/__init__.py` — remove export
- `README.md` — remove deprecated infinite-scroll section
- `pyproject.toml` — patch bump

The agent must not edit domain API repos from this task.

## Execution Notes

_Reserved for the task execution agent._
