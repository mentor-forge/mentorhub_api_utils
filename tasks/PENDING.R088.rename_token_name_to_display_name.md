# R088 – Rename token dict `name` to `display_name`

**Status**: Pending  
**Type**: Feature  
**Depends On**: `none`  
**Description**: Expose the human-readable token label as `display_name` instead of `name` on the dict returned by `create_flask_token()` / `Token.to_dict()`, so domain APIs (starting with F-AA04) can stop using `token.name`. JWT wire claim stays OIDC `name`.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md` — Authentication; `create_flask_token()` claim dict
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `api_utils/flask_utils/token.py` — `Token.to_dict()` currently emits `"name": self.claims.get('name', '')`
- `tests/flask_utils/test_token.py`
- `tests/e2e_auth.py` — E2E JWT still mints OIDC claim `name` (do not rename the JWT claim)
- `../mentorhub/welcome-auth.js` — Developer Edition IdP still signs JWT `name: profile.name` (read-only; do not change that repo)
- `api_utils/services/event_service.py` — `create_event` copies `dict(token)` into Event `context`
- `tests/services/test_event_service.py`, `tests/services/test_notification_service.py`, `tests/services/test_external_event_service.py` — mock flask-token dicts include `"name": "Test User"`
- GitHub: https://github.com/mentor-forge/mentorhub_admin_api/issues/8 (F-AA04; downstream pin is R089 + `ISSUE.mentorhub_admin_api.pin_1_0_1_display_name.md`)

Do **not** bump `pyproject.toml` in this task (R089).

### Mapping rules

- **JWT (wire):** keep the standard OIDC `name` claim. Developer Edition and `tests/e2e_auth.py` continue to mint `name`.
- **Application token dict:** `to_dict()` / `create_flask_token()` must return `display_name` and must **not** include a `name` key.
- Map `display_name` from `claims.get("name")`, falling back to `claims.get("display_name")`, then `""`.
- Do **not** rename Profile/Resource/Path/Plan document `name` fields, list filters, or `get_profile_by_token` (`match={"name": token.user_id}`).
- Do **not** add a compatibility alias (`name` plus `display_name` on the dict). Pre-MVP: replace, do not dual-write.

## Goals

- `Token.to_dict()` and `create_flask_token()` return `display_name` (string, default `""`) and omit `name`.
- JWT claim `name` still round-trips into that `display_name` value.
- `Token.claims` may still contain the raw JWT `name` claim; application code and Event `context` use the dict from `to_dict()`.
- Event `create_event` continues to copy `dict(token)` into `context`, so persisted context uses `display_name` rather than `name`.
- Docstrings on `Token` / `create_flask_token` list `display_name` instead of `name`.
- Mock token dicts that simulate the flask token use `display_name`, not a token-level `name`.

## Testing Expectations

Run all commands from the **api_utils repository root**.

- Update `tests/flask_utils/test_token.py`:
  - `to_dict` / `create_flask_token` assertions use `display_name`.
  - Assert `"name" not in token_dict` for the application dict.
  - Keep asserting `token.claims.get("name")` for the JWT claim when the helper still mints `name`.
  - Cover missing `name` claim → `display_name == ""`.
  - Cover JWT `display_name` without `name` → mapped `display_name`.
- Update mock flask-token dicts in:
  - `tests/services/test_event_service.py`
  - `tests/services/test_notification_service.py`
  - `tests/services/test_external_event_service.py`
- Leave document-field `"name"` fixtures (Profile, Resource, Notification title, etc.) unchanged.
- Leave `tests/e2e_auth.py` JWT payload `name` unchanged.
- `pipenv run test`
- `pipenv run e2e` if a local demo server is running; otherwise note in Execution Notes and rely on unit tests (E2E JWTs still use claim `name`).
- `pipenv run lint` — changed files `black`-clean (repo-wide lint may fail on pre-existing files; do not reformat unrelated files)
- `pipenv run build`

## Outputs

- `api_utils/flask_utils/token.py`
- `tests/flask_utils/test_token.py`
- `tests/services/test_event_service.py` — mock token key only
- `tests/services/test_notification_service.py` — mock token key only
- `tests/services/test_external_event_service.py` — mock token key only

The agent must not update files outside this list.

## Execution Notes
