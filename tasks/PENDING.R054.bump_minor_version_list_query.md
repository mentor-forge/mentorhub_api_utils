# R054 – Bump api-utils minor version for Get List pattern

**Status**: Pending  
**Type**: Feature  
**Depends On**: `R053_deprecate_infinite_scroll`  
**Description**: Bump `api-utils` to `0.5.0` (minor) reflecting new list-query utilities, MongoIO pagination, and service signature extensions.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `README.md` — release process
- `pyproject.toml` — current version `0.4.0`
- `tasks/_PLANNING.md` § Downstream follow-on issues

## Goals

- `pyproject.toml` version → `0.5.0`
- `README.md` changelog or version note summarizing:
  - `MongoIO.get_documents` `skip`/`limit`
  - `list_query` / `list_request` utilities (including `order_spec` / `sort_by`/`order` parsing)
  - `ResourceService`, `PathService`, `NoteService`, `EventService.get_events` list additions/changes
  - `execute_infinite_scroll_query` deprecated (not removed)
- Full test suite green before version bump commit

## Testing Expectations

- `pipenv run db`
- `pipenv run test`
- `pipenv run build`
- `pipenv run lint`

## Outputs

- `pyproject.toml`
- `README.md`

The agent must not update files outside this list.

## Execution Notes

_Reserved for the task execution agent._
