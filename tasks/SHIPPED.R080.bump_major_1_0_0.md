# R080 – Bump major 1.0.0 and document extend + RBAC

**Status**: Shipped  
**Type**: Feature  
**Depends On**: `R076_shared_profile_get_and_create`, `R077_shared_notification_get_and_create`, `R078_strip_journey_control_mutations`, `R079_strip_remaining_control_mutations`, `R081_outbound_rbac_helper`, `R082_apply_outbound_rbac_to_shared_gets`  
**Description**: Publish F-UA13 (shared GET + global POST; API subclasses own mutate/enrich) and F-UA12 (outbound filters in utils) as **major** `1.0.0`. Document how domain APIs extend shared services, add inbound write RBAC, and point routes at the local subclass.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root.

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/Specifications/architecture.yaml`
- `README.md` — **Release and publish**; current pin example `api-utils==0.7.1`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- `tasks/ISSUE.journey_api.md` and sibling `tasks/ISSUE.*.md` from this feature (downstream only; do not execute)
- `tasks/SHIPPED.R072.export_ingress_services_bump_minor.md` — bump pattern (this task is **major**, not minor)
- `pyproject.toml` — current `version` (expected `0.7.1` at planning time unless earlier tasks already bumped; if so, still set **`1.0.0`**)
- `api_utils/__init__.py`
- `api_utils/services/__init__.py`

### Versioning

- **Major** bump: breaking surface (control mutations left domain APIs; outbound GET filters; get-by-id 404 when hidden). Target **`1.0.0`**. Do not ship `0.8.0`.
- Publishing is after PR merge via `pipenv run tag-release` — not in this task.

### README must show

Domain API subclass + **inbound** write check + route import:

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

State clearly:

- Shared GET/list apply **outbound** filters (admin root; `status != archived`; token `profile_id` / `customer_id` / `mentor_id`). Get-by-id uses the same filter post-fetch (404).
- Shared global POST: Event, Notification, Profile.
- API subclass: enrich, control POST/PATCH/mutate, **inbound** who-may-write.
- Routes import the local subclass.
- Point planners at `tasks/ISSUE.journey_api.md` and the other `ISSUE.*` artifacts (pin `api-utils==1.0.0`).

`api_utils/__init__.py` / `services/__init__.py` keep exporting the same service class names. Downstream subclasses import those names. Export the outbound helper if R081 added it to a package `__all__`.

## Goals

- `pyproject.toml` version is `1.0.0`.
- README pin examples and services docs match the split, outbound RBAC, and extend + inbound pattern.
- `pipenv run python -c "from api_utils.services import JourneyService, ProfileService, NotificationService, EventService"` still works.
- Build artifact name reflects `1.0.0`.

## Testing Expectations

- `pipenv run test`
- `pipenv run lint` — R080 files `black`-clean
- `pipenv run build` — e.g. `api_utils-1.0.0-...`
- Import smoke: `pipenv run python -c "from api_utils.services import JourneyService, EventService, NotificationService, ProfileService"`

## Outputs

- `pyproject.toml`
- `README.md`
- `api_utils/__init__.py` — only if export list/comments need a contract note
- `api_utils/services/__init__.py` — only if the package docstring needs a pointer update

The agent must not update files outside this list.

## Execution Notes

- Bumped `pyproject.toml` `version` `0.7.1` → `1.0.0` (major: control mutations moved to domain API subclasses; outbound GET filters; get-by-id 404 when hidden).
- `README.md`: pin example `api-utils==1.0.0`; expanded **Data-boundary contract** with outbound vs inbound RBAC split, subclass + `_check_permission` + route import example, and **Downstream planning artifacts** linking six `ISSUE.*` files with `api-utils==1.0.0` pin guidance.
- `api_utils/services/__init__.py`: package docstring updated for outbound filters (`build_outbound_match`, `require_outbound`) and inbound write checks on domain subclasses; rbac helpers already exported in `__all__` from R081 — no export changes.
- `api_utils/__init__.py`: unchanged (no version constant; service exports unchanged).
- `pipenv run test`: **225 passed**, 23 deselected.
- `pipenv run lint`: failed on 24 pre-existing files (not R080 outputs); `black --check api_utils/services/__init__.py`: clean.
- `pipenv run build`: `api_utils-1.0.0.tar.gz` and `api_utils-1.0.0-py3-none-any.whl`.
- Import smoke: `JourneyService`, `EventService`, `NotificationService`, `ProfileService` import OK.
