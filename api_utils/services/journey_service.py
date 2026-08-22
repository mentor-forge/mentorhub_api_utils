"""
Journey service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Journey domain.
"""

import logging

from bson import ObjectId
from bson.errors import InvalidId

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.services.rbac import (
    EMPTY_SCOPE_MATCH,
    build_outbound_match,
    matches_outbound,
    require_outbound,
)

logger = logging.getLogger(__name__)

ARCHIVED_STATUS = "archived"
JOURNEY_ID_PROPERTIES = ["_id", "profile_id"]

TEMPLATE_JOURNEY_ID = "ffff00000000000000000001"


class JourneyService:
    """Service class for Journey domain operations."""

    @classmethod
    def _check_permission(cls, token, operation, journey_id=None):
        if operation == "read":
            return

    @classmethod
    def _journey_identity_or(cls, token):
        """Own-profile scope; Journey has no customer/mentor fields today."""
        profile_id = token.get("profile_id")
        if not profile_id:
            return EMPTY_SCOPE_MATCH

        or_clauses = []
        for field in ("profile_id", "_id"):
            clause = {field: profile_id}
            encode_document(clause, JOURNEY_ID_PROPERTIES, [])
            or_clauses.append(clause)
        return {"$or": or_clauses}

    @classmethod
    def _outbound_match(cls, token):
        return build_outbound_match(
            token,
            [
                {"status": {"$ne": ARCHIVED_STATUS}},
                cls._journey_identity_or(token),
            ],
        )

    @classmethod
    def _validate_object_id(cls, value, field_name):
        try:
            ObjectId(value)
        except (InvalidId, TypeError):
            raise HTTPBadRequest(f"{field_name} must be a valid MongoDB ObjectId")

    @classmethod
    def _oid(cls, value):
        """Coerce an id to its canonical BSON ``ObjectId`` form."""
        return ObjectId(value)

    @classmethod
    def get_journey(cls, journey_id, token, breadcrumb):
        try:
            cls._check_permission(token, "read")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            journey = mongo.get_document(config.JOURNEY_COLLECTION_NAME, journey_id)
            require_outbound(
                journey,
                cls._outbound_match(token),
                not_found_message=f"Journey {journey_id} not found",
            )
            return journey
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving journey {journey_id}: {e}")
            raise HTTPInternalServerError(f"Failed to retrieve journey {journey_id}")

    @classmethod
    def get_journey_progress(cls, profile_id, token, breadcrumb):
        """
        Count the resources in a mentee's active Learning Journey by scope.

        Returns a dict with ``library``, ``now``, and ``next`` counts.
        ``library`` and ``now`` count their resource entries directly; ``next``
        sums the resource entries across all Next topics. Returns zeros when the
        mentee has no active journey or the journey is not visible to the caller.
        """
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        match = {"profile_id": profile_id, "status": "active"}
        encode_document(match, JOURNEY_ID_PROPERTIES, [])
        journeys = mongo.get_documents(
            config.JOURNEY_COLLECTION_NAME,
            match=match,
        )
        if not journeys:
            return {"library": 0, "now": 0, "next": 0}

        journey = journeys[0]
        outbound = cls._outbound_match(token)
        if not matches_outbound(journey, outbound):
            return {"library": 0, "now": 0, "next": 0}

        next_resources = sum(
            len(topic.get("resources") or []) for topic in (journey.get("next") or [])
        )
        return {
            "library": len(journey.get("library") or []),
            "now": len(journey.get("now") or []),
            "next": next_resources,
        }
