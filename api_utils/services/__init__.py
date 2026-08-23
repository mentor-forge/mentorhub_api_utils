"""
Shared domain service implementations for Mentor Hub APIs.

Architecture (controls / creates / consumes)
--------------------------------------------
One service domain **controls** a collection; any domain may **consume**
(GET) that collection or **create** immutable documents in it. Shared
services therefore own:

- GET / list with **outbound** RBAC (``build_outbound_match``,
  ``require_outbound`` from ``api_utils.services.rbac``): admin is
  unrestricted; non-admin callers are scoped by token ``profile_id`` /
  ``customer_id`` / ``mentor_id`` and ``status != archived``. Get-by-id
  applies the same match after fetch (404 when hidden).
- Global POSTs that any journey domain may issue:
  ``EventService.create_event``,
  ``NotificationService.create_notification``,
  ``ProfileService.create_profile``

Domain API subclasses own enrich, control POST, PATCH / PUT, and mutate
for collections that domain **controls**, plus **inbound** who-may-write
checks (who may PATCH or mutate — not outbound visibility). They extend
these classes (``class JourneyService(api_utils.services.JourneyService)``)
so overrides dispatch through ``cls``. Routes import the local API
subclass, not ``api_utils.services`` directly.

See ``README.md`` and ``tasks/SHIPPED_ISSUE.journey_api.md`` for extend patterns.
"""

from api_utils.services.aggregation_service import AggregationService
from api_utils.services.encounter_service import EncounterService
from api_utils.services.event_service import EventService
from api_utils.services.external_event_service import ExternalEventService
from api_utils.services.journey_service import JourneyService, TEMPLATE_JOURNEY_ID
from api_utils.services.mentee_service import MenteeService
from api_utils.services.note_service import NoteService
from api_utils.services.notification_service import NotificationService
from api_utils.services.path_service import PathService
from api_utils.services.plan_service import PlanService
from api_utils.services.profile_service import ProfileService
from api_utils.services.resource_service import ResourceService
from api_utils.services.rbac import (
    EMPTY_SCOPE_MATCH,
    and_match,
    build_outbound_match,
    is_admin,
    matches_outbound,
    require_outbound,
)

__all__ = [
    "AggregationService",
    "EncounterService",
    "EventService",
    "ExternalEventService",
    "JourneyService",
    "MenteeService",
    "NoteService",
    "NotificationService",
    "PathService",
    "PlanService",
    "ProfileService",
    "ResourceService",
    "TEMPLATE_JOURNEY_ID",
    "EMPTY_SCOPE_MATCH",
    "and_match",
    "build_outbound_match",
    "is_admin",
    "matches_outbound",
    "require_outbound",
]
