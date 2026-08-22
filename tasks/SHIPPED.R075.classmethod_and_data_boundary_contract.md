# R075 – Classmethod services and data-boundary contract

**Status**: Shipped  
**Type**: Feature  
**Depends On**: none  
**Description**: Convert shared service methods from `@staticmethod` to `@classmethod` so domain API subclasses can extend and override them, and document the Architecture `controls` / `creates` / `consumes` split in the services package.

## Path anchoring

All paths below are relative to the **mentorhub_api_utils** repository root (the directory that contains `Pipfile`).

- Standards: `../mentorhub/DeveloperEdition/standards/api_standards.md`
- Architecture: `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md`, `../mentorhub/Specifications/architecture.yaml`
- In-repo: `README.md`, `api_utils/services/`, `tests/services/`, `tasks/`

## Context

Always read these files before implementation:

- `../mentorhub/DeveloperEdition/standards/api_standards.md`
- `../mentorhub/DeveloperEdition/standards/ArchitecturePrinciples.md` — **Bounded Domains**
- `../mentorhub/Specifications/architecture.yaml` — `data_domains.controls` / `creates` / `consumes`
- `README.md`
- `tasks/_PLANNING.md`
- `tasks/_ORCHESTRATE.md`
- Every module under `api_utils/services/`
- `api_utils/services/__init__.py`

### Data boundary (this task is free-standing)

From Architecture Principles: one service domain **controls** a collection; any domain may **consume** (GET) or **create immutable** documents. From `architecture.yaml`: Event is created by every journey domain; Notification is controlled by Discovery but any domain may POST; Profile is controlled by Customer and created by Admin and Customer. Shared services therefore own GET/list (RBAC `base_match`) plus those global POSTs. Domain API subclasses own enrich, control POST, PATCH, and mutate. Routes import the local subclass. **Depends On** on each PENDING task is the sequencer — do not edit `_PLANNING.md` or `_ORCHESTRATE.md`.

### Why classmethod

Domain APIs must **extend** shared services (`class JourneyService(api_utils.services.JourneyService)`). Internal calls that use the hard-coded class name (`JourneyService._check_permission(...)`) never dispatch to the subclass. Convert public and helper methods to `@classmethod` and call `cls.*` so RBAC, enrich, and mutate overrides work.

Do **not** remove or move methods in this task — R076–R079 strip mutations.

### Contract to document (package docstring + README)

- Shared: GET / list with an RBAC `base_match` derived from the token.
- Shared global POST: `EventService.create_event`, `NotificationService.create_notification`, `ProfileService.create_profile` (added in R076).
- Domain API subclass: enrich, control POST, PATCH / PUT / mutate for collections that domain **controls**.
- Routes import the API subclass, not `api_utils.services` directly.

## Goals

- Every service method that is currently `@staticmethod` becomes `@classmethod` with `cls` as the first parameter; intra-class calls use `cls`.
- `EventService` is already the global-POST + GET reference — leave its surface unchanged aside from the classmethod conversion.
- `api_utils/services/__init__.py` module docstring states the data-boundary contract and the extend/routes rule.
- `README.md` **Shared domain services** section describes the contract in one short subsection (no version bump in this task).
- Existing unit tests still pass (patch targets remain on the class).

## Testing Expectations

Run all commands from the **api_utils repository root**.

- `pipenv run test tests/services/`
- `pipenv run test`
- `pipenv run lint` — new/edited files must be `black`-clean; do not churn unrelated pre-existing lint
- `pipenv run build`

## Outputs

- `api_utils/services/aggregation_service.py`
- `api_utils/services/encounter_service.py`
- `api_utils/services/event_service.py`
- `api_utils/services/external_event_service.py`
- `api_utils/services/journey_service.py`
- `api_utils/services/mentee_service.py`
- `api_utils/services/note_service.py`
- `api_utils/services/notification_service.py`
- `api_utils/services/path_service.py`
- `api_utils/services/plan_service.py`
- `api_utils/services/profile_service.py`
- `api_utils/services/resource_service.py`
- `api_utils/services/__init__.py` — contract docstring
- `README.md` — Shared domain services subsection
- `tests/services/*.py` — only if a test breaks because of the classmethod conversion

The agent must not update files outside this list.

## Execution Notes

### Plan
1. Convert every `@staticmethod` on shared service classes under `api_utils/services/` to `@classmethod` with `cls` as the first parameter.
2. Rewrite intra-class calls (`JourneyService._check_permission`, `AggregationService._parse_iso_duration`, …) to `cls.*` so domain API subclasses can override helpers and public methods.
3. Leave inter-class service-to-service calls (`NoteService.create_note` from Aggregation, `PlanService.get_plan` from Encounter, …) on the imported class names.
4. Do not remove, move, or add methods — mutation stripping is R076–R079.
5. Document the Architecture controls/creates/consumes split and extend/routes rule in `api_utils/services/__init__.py` and a short README subsection under Shared domain services.
6. No version bump. Change tests only if the classmethod conversion breaks them.
7. Run `pipenv run test tests/services/`, `pipenv run test`, `pipenv run lint`, and `pipenv run build`.

### Summary

All 13 modules under `api_utils/services/` were converted: every method on every
shared service class is now a `@classmethod` taking `cls` as its first
parameter. An AST sweep over `api_utils/services/*.py` confirms zero remaining
`@staticmethod` declarations and zero methods whose first parameter is not
`cls`.

Intra-class calls were rewritten from the hard-coded class name to `cls.*` so
domain API subclasses can override RBAC, enrich, and mutate behavior and have
internal call sites dispatch to the override — for example
`JourneyService._check_permission(...)` → `cls._check_permission(...)`,
`AggregationService._get_or_create_aggregation(...)` →
`cls._get_or_create_aggregation(...)`, and
`ProfileService._resource_ref(...)` → `cls._resource_ref(...)`.

Inter-class service-to-service calls were deliberately left on the imported
class names (per plan step 3), because those resolve a *different* domain's
service and must not follow the calling subclass. The remaining cross-class
references are `NoteService` and `PlanService` from Encounter/Aggregation,
`EventService` and `AggregationService` from Journey/Event, `ResourceService`
from Path, and `JourneyService` / `EncounterService` / `MenteeService` from
Profile.

No methods were removed, moved, or added — mutation stripping stays with
R076–R079. `EventService`'s surface is unchanged aside from the classmethod
conversion. No version bump (`pyproject.toml` untouched, still `0.7.1`).

Documentation: the `api_utils/services/__init__.py` module docstring now states
the Architecture controls / creates / consumes split, the shared GET/list plus
global-POST surface (`EventService.create_event`,
`NotificationService.create_notification`, `ProfileService.create_profile`),
and the extend/routes rule. `README.md` gained a short **Data-boundary
contract** subsection under **Shared domain services** carrying the same
contract. Both were cross-checked against `architecture.yaml`: Profile is
controlled by Customer and created by Admin, Notification is controlled by
Discovery, and Event is created by every journey domain.

No test files required changes. `mock.patch` targets remain valid because the
methods still live on the same classes, and `@classmethod` is transparent to
call sites that invoke through the class.

### Test results

Run from the api_utils repository root:

- `pipenv run test tests/services/` — **pass** (273 passed, 24 deselected)
- `pipenv run test` — **pass** (273 passed, 24 deselected)
- `pipenv run lint` — **pre-existing failures only** (exit 1). `black --check`
  reports 24 files it would reformat; none are files this task touched. All 13
  files under `api_utils/services/` are black-clean
  (`black --check api_utils/services/` → exit 0, 13 files unchanged). The 24
  flagged files are unmodified relative to `HEAD`, so the lint debt predates
  this task and was intentionally not churned.
- `pipenv run build` — **pass** (built `api_utils-0.7.1.tar.gz` and
  `api_utils-0.7.1-py3-none-any.whl`)
