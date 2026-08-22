"""
Mentee service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for the Mentee domain. A Mentee
document holds the mentor's notes about a single mentee, keyed by the mentee's
Profile id.

Per the API standards (separation of concerns), this service contains business
logic only. It raises the appropriate domain exceptions (e.g. HTTPForbidden,
HTTPNotFound); the route layer's ``@handle_route_exceptions`` wrapper is
responsible for translating those, and any unexpected error, into HTTP
responses.
"""

from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.services.rbac import is_admin, matches_outbound
from bson import ObjectId
from bson.errors import InvalidId
import logging

logger = logging.getLogger(__name__)

ARCHIVED_STATUS = "archived"
MENTEE_ID_PROPERTIES = ["profile_id"]


class MenteeService:
    """
    Service class for Mentee domain operations (read-only in shared api_utils).

    Handles:
    - Outbound RBAC visibility on shared GET
    - MongoDB operations via MongoIO singleton
    - Read-only lookup of the mentee-notes document (404 if missing or hidden)
    """

    @classmethod
    def _collection_name(cls, config):
        """Resolve the Mentee collection name from shared config."""
        return config.MENTEE_COLLECTION_NAME

    @classmethod
    def _check_permission(cls, token, operation):
        """Shared reads require a valid token only; outbound filtering applies separately."""
        pass

    @classmethod
    def _own_profile_match(cls, token):
        profile_id = token.get("profile_id")
        if not profile_id:
            return None
        clause = {"profile_id": profile_id}
        from api_utils.mongo_utils import encode_document

        encode_document(clause, MENTEE_ID_PROPERTIES, [])
        return clause

    @classmethod
    def _is_archived(cls, document):
        status = document.get("status")
        return status is not None and status == ARCHIVED_STATUS

    @classmethod
    def _mentor_of_profile(cls, profile_id, token):
        """Return True when the caller is the mentor assigned to ``profile_id``."""
        mentor_id = token.get("mentor_id")
        token_profile_id = token.get("profile_id")
        if not mentor_id and not token_profile_id:
            return False

        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        profile = mongo.get_document(config.PROFILE_COLLECTION_NAME, str(profile_id))
        if profile is None:
            return False

        profile_mentor_id = profile.get("mentor_id")
        if mentor_id and str(profile_mentor_id) == str(mentor_id):
            return True
        if token_profile_id and str(profile_mentor_id) == str(token_profile_id):
            return True
        return False

    @classmethod
    def _require_mentee_visible(cls, document, token, profile_id):
        if document is None:
            raise HTTPNotFound(f"Mentee for profile {profile_id} not found")
        if is_admin(token):
            return document
        if cls._is_archived(document):
            raise HTTPNotFound(f"Mentee for profile {profile_id} not found")

        own_match = cls._own_profile_match(token)
        if own_match and matches_outbound(document, own_match):
            return document

        doc_profile_id = document.get("profile_id")
        if cls._mentor_of_profile(doc_profile_id, token):
            return document

        raise HTTPNotFound(f"Mentee for profile {profile_id} not found")

    @classmethod
    def _to_object_id(cls, value, label):
        """
        Convert a string id to a BSON ``ObjectId``.

        Args:
            value: The id value to convert
            label: Human-readable field name used in error messages

        Returns:
            ObjectId: The converted id

        Raises:
            HTTPBadRequest: If the value is not a valid ObjectId
        """
        try:
            return ObjectId(value)
        except (InvalidId, TypeError):
            raise HTTPBadRequest(f"Invalid {label}: {value}")

    @classmethod
    def get_mentee(cls, profile_id, token, breadcrumb):
        """
        Retrieve the mentee-notes document for a Profile.

        Looks up the Mentee document by ``profile_id``. Returns 404 when no
        document exists or the caller cannot see it; create-if-missing belongs
        on the Mentor API subclass.

        Args:
            profile_id: The mentee Profile id (string ObjectId)
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for audit/logging

        Returns:
            dict: The existing Mentee document

        Raises:
            HTTPBadRequest: If profile_id is not a valid ObjectId
            HTTPNotFound: If no Mentee document exists or is not visible
        """
        try:
            cls._check_permission(token, "read")
            profile_object_id = cls._to_object_id(profile_id, "profile_id")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            collection_name = cls._collection_name(config)

            existing = mongo.get_documents(
                collection_name, match={"profile_id": profile_object_id}
            )
            document = existing[0] if existing else None
            result = cls._require_mentee_visible(document, token, profile_id)

            logger.info(
                f"Retrieved mentee for profile {profile_id} "
                f"for user {token.get('user_id')}"
            )
            return result
        except (HTTPBadRequest, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error retrieving mentee for profile {profile_id}: {str(e)}")
            raise HTTPInternalServerError(
                f"Failed to retrieve mentee for profile {profile_id}"
            )
