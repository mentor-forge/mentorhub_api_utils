"""
Flask blueprint factories for shared consume GET endpoints.

Each factory accepts a local service subclass (``service_cls``); factories
must not default to ``api_utils.services`` classes so domain APIs bind their
own subclass explicitly.
"""

from __future__ import annotations

import importlib
import logging

from flask import Blueprint, jsonify, request

from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.exceptions import HTTPBadRequest
from api_utils.flask_utils.list_request import (
    parse_list_request,
    parse_pagination_headers,
)
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from api_utils.flask_utils.token import create_flask_token

logger = logging.getLogger(__name__)


def _auth_context():
    """Create token and breadcrumb for a route handler."""
    token = create_flask_token()
    breadcrumb = create_flask_breadcrumb(token)
    return token, breadcrumb


def _json_ok(data):
    """Return a 200 JSON response."""
    return jsonify(data), 200


def _module_attr(service_cls, attr_name, default=None):
    """Resolve a list-spec constant from the service class or its bases."""
    for cls in service_cls.__mro__:
        module = importlib.import_module(cls.__module__)
        if hasattr(module, attr_name):
            return getattr(module, attr_name)
    return default


def create_resource_get_routes(service_cls, *, name="resource_routes"):
    """GET list + GET by resource_id."""
    bp = Blueprint(name, __name__)
    filter_spec = _module_attr(service_cls, "RESOURCE_LIST_FILTERS")
    order_spec = _module_attr(service_cls, "RESOURCE_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_resources():
        token, breadcrumb = _auth_context()
        offset, size, filters, sort_by = parse_list_request(
            request, filter_spec, order_spec
        )
        resources = service_cls.get_resources(
            token, breadcrumb, offset, size, filters, sort_by
        )
        logger.info(
            f"get_resources Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(resources)

    @bp.route("/<resource_id>", methods=["GET"])
    @handle_route_exceptions
    def get_resource(resource_id):
        token, breadcrumb = _auth_context()
        resource = service_cls.get_resource(resource_id, token, breadcrumb)
        logger.info(
            f"get_resource Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(resource)

    logger.info("Resource GET Flask Routes Registered")
    return bp


def create_path_get_routes(service_cls, *, name="path_routes"):
    """GET list + GET by path_id."""
    bp = Blueprint(name, __name__)
    filter_spec = _module_attr(service_cls, "PATH_LIST_FILTERS")
    order_spec = _module_attr(service_cls, "PATH_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_paths():
        token, breadcrumb = _auth_context()
        offset, size, filters, sort_by = parse_list_request(
            request, filter_spec, order_spec
        )
        paths = service_cls.get_paths(token, breadcrumb, offset, size, filters, sort_by)
        logger.info(
            f"get_paths Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(paths)

    @bp.route("/<path_id>", methods=["GET"])
    @handle_route_exceptions
    def get_path(path_id):
        token, breadcrumb = _auth_context()
        path = service_cls.get_path(path_id, token, breadcrumb)
        logger.info(
            f"get_path Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(path)

    logger.info("Path GET Flask Routes Registered")
    return bp


def create_plan_get_routes(service_cls, *, name="plan_routes"):
    """GET list + GET by plan_id."""
    bp = Blueprint(name, __name__)
    filter_spec = _module_attr(service_cls, "PLAN_LIST_FILTERS")
    order_spec = _module_attr(service_cls, "PLAN_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_plans():
        token, breadcrumb = _auth_context()
        offset, size, filters, sort_by = parse_list_request(
            request, filter_spec, order_spec
        )
        plans = service_cls.get_plans(token, breadcrumb, offset, size, filters, sort_by)
        logger.info(
            f"get_plans Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(plans)

    @bp.route("/<plan_id>", methods=["GET"])
    @handle_route_exceptions
    def get_plan(plan_id):
        token, breadcrumb = _auth_context()
        plan = service_cls.get_plan(plan_id, token, breadcrumb)
        logger.info(
            f"get_plan Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(plan)

    logger.info("Plan GET Flask Routes Registered")
    return bp


def create_profile_get_routes(service_cls, *, name="profile_routes"):
    """GET list + GET by profile_id."""
    bp = Blueprint(name, __name__)
    filter_spec = _module_attr(service_cls, "PROFILE_LIST_FILTERS")
    order_spec = _module_attr(service_cls, "PROFILE_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_profiles():
        token, breadcrumb = _auth_context()
        offset, size, filters, sort_by = parse_list_request(
            request, filter_spec, order_spec
        )
        profiles = service_cls.get_profiles(
            token, breadcrumb, offset, size, filters, sort_by
        )
        logger.info(
            f"get_profiles Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(profiles)

    @bp.route("/<profile_id>", methods=["GET"])
    @handle_route_exceptions
    def get_profile(profile_id):
        token, breadcrumb = _auth_context()
        profile = service_cls.get_profile(profile_id, token, breadcrumb)
        logger.info(
            f"get_profile Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(profile)

    logger.info("Profile GET Flask Routes Registered")
    return bp


def create_notification_get_routes(service_cls, *, name="notification_routes"):
    """GET list only."""
    bp = Blueprint(name, __name__)
    order_spec = _module_attr(service_cls, "NOTIFICATION_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_notifications():
        token, breadcrumb = _auth_context()
        offset, size, _, _ = parse_list_request(request, {}, order_spec)
        notifications = service_cls.get_notifications(
            token, breadcrumb, offset=offset, size=size
        )
        logger.info(
            f"get_notifications Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(notifications)

    logger.info("Notification GET Flask Routes Registered")
    return bp


def create_event_get_routes(service_cls, *, name="event_routes"):
    """GET list only; optional profile_id query narrows scope."""
    bp = Blueprint(name, __name__)
    filter_spec = _module_attr(service_cls, "EVENT_LIST_FILTERS")
    order_spec = _module_attr(service_cls, "EVENT_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_events():
        token, breadcrumb = _auth_context()
        offset, size, filters, sort_by = parse_list_request(
            request, filter_spec, order_spec
        )
        profile_id = request.args.get("profile_id")
        kwargs = {}
        if profile_id is not None:
            kwargs["profile_id"] = profile_id
        events = service_cls.get_events(
            token, breadcrumb, offset, size, filters, sort_by, **kwargs
        )
        logger.info(
            f"get_events Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(events)

    logger.info("Event GET Flask Routes Registered")
    return bp


def create_note_get_routes(service_cls, *, name="note_routes"):
    """GET list scoped by required resource_id query param."""
    bp = Blueprint(name, __name__)
    filter_spec = _module_attr(service_cls, "NOTE_LIST_FILTERS")
    order_spec = _module_attr(service_cls, "NOTE_LIST_ORDER")

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_notes():
        token, breadcrumb = _auth_context()
        resource_id = request.args.get("resource_id")
        if not resource_id:
            raise HTTPBadRequest("resource_id query parameter is required")
        offset, size, filters, sort_by = parse_list_request(
            request, filter_spec, order_spec
        )
        notes = service_cls.get_notes_for_resource(
            resource_id, token, breadcrumb, offset, size, filters, sort_by
        )
        logger.info(
            f"get_notes Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(notes)

    logger.info("Note GET Flask Routes Registered")
    return bp


def create_journey_get_routes(service_cls, *, name="journey_routes"):
    """GET by journey_id only (list owned by Mentee get-or-create)."""
    bp = Blueprint(name, __name__)

    @bp.route("/<journey_id>", methods=["GET"])
    @handle_route_exceptions
    def get_journey(journey_id):
        token, breadcrumb = _auth_context()
        journey = service_cls.get_journey(journey_id, token, breadcrumb)
        logger.info(
            f"get_journey Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(journey)

    logger.info("Journey GET Flask Routes Registered")
    return bp


def create_encounter_get_routes(service_cls, *, name="encounter_routes"):
    """GET list scoped by required mentee_id + GET by encounter_id."""
    bp = Blueprint(name, __name__)

    @bp.route("", methods=["GET"])
    @handle_route_exceptions
    def get_encounters():
        token, breadcrumb = _auth_context()
        mentee_id = request.args.get("mentee_id")
        if not mentee_id:
            raise HTTPBadRequest("mentee_id query parameter is required")
        offset, size = parse_pagination_headers(request)
        encounters = service_cls.get_encounters_for_mentee(
            mentee_id, token, breadcrumb, offset, size
        )
        logger.info(
            f"get_encounters Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(encounters)

    @bp.route("/<encounter_id>", methods=["GET"])
    @handle_route_exceptions
    def get_encounter(encounter_id):
        token, breadcrumb = _auth_context()
        encounter = service_cls.get_encounter(encounter_id, token, breadcrumb)
        logger.info(
            f"get_encounter Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(encounter)

    logger.info("Encounter GET Flask Routes Registered")
    return bp


def create_mentee_get_routes(service_cls, *, name="mentee_routes"):
    """GET by profile_id only."""
    bp = Blueprint(name, __name__)

    @bp.route("/<profile_id>", methods=["GET"])
    @handle_route_exceptions
    def get_mentee(profile_id):
        token, breadcrumb = _auth_context()
        mentee = service_cls.get_mentee(profile_id, token, breadcrumb)
        logger.info(
            f"get_mentee Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(mentee)

    logger.info("Mentee GET Flask Routes Registered")
    return bp


def create_aggregation_get_routes(service_cls, *, name="aggregation_routes"):
    """GET aggregation document by resource_id."""
    bp = Blueprint(name, __name__)

    @bp.route("/<resource_id>", methods=["GET"])
    @handle_route_exceptions
    def get_aggregation(resource_id):
        token, breadcrumb = _auth_context()
        aggregation = service_cls.get_aggregation_for_resource(
            resource_id, token, breadcrumb
        )
        logger.info(
            f"get_aggregation Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(aggregation)

    logger.info("Aggregation GET Flask Routes Registered")
    return bp


def create_external_event_get_routes(service_cls, *, name="external_event_routes"):
    """GET by event_id only."""
    bp = Blueprint(name, __name__)

    @bp.route("/<event_id>", methods=["GET"])
    @handle_route_exceptions
    def get_external_event(event_id):
        token, breadcrumb = _auth_context()
        event = service_cls.get_external_event(event_id, token, breadcrumb)
        logger.info(
            f"get_external_event Success {breadcrumb['at_time']}, {breadcrumb['correlation_id']}"
        )
        return _json_ok(event)

    logger.info("External Event GET Flask Routes Registered")
    return bp
