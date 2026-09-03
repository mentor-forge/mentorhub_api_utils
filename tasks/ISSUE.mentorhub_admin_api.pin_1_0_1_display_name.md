Please create @_PLANNING.md tasks to implement this issue. Only create tasks, do not edit any files outside of the @tasks folder.

**GitHub**: https://github.com/mentor-forge/mentorhub_admin_api/issues/8

# F-AA04: Pin api-utils 1.0.1 and use token.display_name

Follows **F-AA03** (pin `api-utils==1.0.0`). This issue owns the bump to **`1.0.1`**.

Do **not** implement this from `mentorhub_api_utils` orchestration. Plan and execute in `mentorhub_admin_api` after `api-utils==1.0.1` is published (`tag-release` on the utils repo).

## Summary

`api_utils` 1.0.1 changes the flask token dict from `name` to **`display_name`**. JWT wire claim remains OIDC `name` (Developer Edition `welcome-auth.js` and each API’s `e2e_auth.py` keep minting `name`). `create_flask_token()` maps that claim to `token["display_name"]` and no longer emits `token["name"]`.

Admin API must pin **`api-utils==1.0.1`** and replace any use of `token.name` / `token["name"]` / `token.get("name")` on the **flask token dict** with `display_name`.

Do **not** rename Profile, Customer, Setting, or other **document** `name` fields.

## Pin (this issue owns the bump)

- Set `api-utils==1.0.1` in `Pipfile` / `Pipfile.lock` (currently `==1.0.0` after F-AA03).
- `pipenv run install` (CodeArtifact auth; run `mh` first if needed). Do **not** use bare `pipenv install`.

## Token dict

Search Admin API `src/` and `test/` for flask-token usage:

- `token["name"]`, `token.get("name")`, `token.name` on the dict from `create_flask_token()` or mocks of it
- Mock `create_flask_token` return values that include `"name": "..."` as a **token** field (not a domain document)

Replace those keys with `display_name`.

Leave unchanged:

- JWT payload claim `"name"` in `test/e2e/e2e_auth.py` (and any other JWT minting helpers)
- Cognito/Stripe webhook `userAttributes.name` and Profile/Customer/Setting document `name`
- List filters / OpenAPI `name` query params

Event create copies `dict(token)` into Event `context`. After the pin, persisted context will contain `display_name` instead of `name` if the token dict is passed through. Update assertions only if tests inspect that key.

## Acceptance

- `Pipfile` pins `api-utils==1.0.1`.
- No flask-token dict uses `name` for the display label; they use `display_name`.
- Domain document `name` fields are unchanged.
- `pipenv run test`, `pipenv run lint`, `pipenv run build`.
