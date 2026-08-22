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
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)

logger = logging.getLogger(__name__)

TEMPLATE_JOURNEY_ID = "ffff00000000000000000001"


class JourneyService:
    """Service class for Journey domain operations."""

    @classmethod
    def _check_permission(cls, token, operation, journey_id=None):
        if operation == "read":
            return

    @classmethod
    def _validate_object_id(cls, value, field_name):
        try:
            ObjectId(value)
        except (InvalidId, TypeError):
            raise HTTPBadRequest(f"{field_name} must be a valid MongoDB ObjectId")

    @classmethod
    def _oid(cls, value):
        """Coerce an id to its canonical BSON ``ObjectId`` form.

        Inbound ids arrive as strings while stored ids are ``ObjectId``;
        ``ObjectId(...)`` accepts both, so this yields a single canonical type
        for in-memory equality checks. Persistence is handled separately by
        ``encode_document`` at the ``MongoIO`` boundary, so services never write
        the string form back into a document.
        """
        return ObjectId(value)

    @classmethod
    def get_journey(cls, journey_id, token, breadcrumb):
        try:
            cls._check_permission(token, "read")
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            journey = mongo.get_document(config.JOURNEY_COLLECTION_NAME, journey_id)
            if journey is None:
                raise HTTPNotFound(f"Journey {journey_id} not found")
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
        mentee has no active journey.

        Unlike the generic Journey reads (which are open), the Mentor Dashboard
        progress aggregation is gated to the ``mentor`` or ``admin`` role, so the
        role check is performed inline here rather than through the shared
        ``_check_permission(token, "read")`` (which intentionally allows open
        reads for the mentee-facing Journey surface).

        Args:
            profile_id: The mentee Profile id whose journey progress is wanted
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for audit/logging

        Returns:
            dict: ``{"library": int, "now": int, "next": int}``

        Raises:
            HTTPForbidden: If the caller does not hold the ``mentor`` or
                ``admin`` role
        """
        config = Config.get_instance()
        allowed_roles = {config.ROLE_MENTOR, config.ROLE_ADMIN}
        roles = token.get("roles", []) or []
        if not allowed_roles.intersection(roles):
            raise HTTPForbidden("Mentor or admin role required to access journey data")

        mongo = MongoIO.get_instance()
        # Journey.profile_id is stored as a BSON ObjectId (see Mentee clone),
        # so encode the match id before querying. MongoIO.get_documents does not
        # coerce match values (unlike get_document/update_document), so a raw
        # string profile_id would silently match nothing. A value that is
        # already an ObjectId is left unchanged by encode_document.
        match = {"profile_id": profile_id, "status": "active"}
        encode_document(match, ["profile_id"], [])
        journeys = mongo.get_documents(
            config.JOURNEY_COLLECTION_NAME,
            match=match,
        )
        if not journeys:
            return {"library": 0, "now": 0, "next": 0}

        journey = journeys[0]
        next_resources = sum(
            len(topic.get("resources") or []) for topic in (journey.get("next") or [])
        )
        return {
            "library": len(journey.get("library") or []),
            "now": len(journey.get("now") or []),
            "next": next_resources,
        }
