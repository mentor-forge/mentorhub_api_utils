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
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)
from bson import ObjectId
from bson.errors import InvalidId
import logging

logger = logging.getLogger(__name__)


class MenteeService:
    """
    Service class for Mentee domain operations (read-only in shared api_utils).

    Handles:
    - RBAC authorization checks (requires the ``mentor`` or ``admin`` role)
    - MongoDB operations via MongoIO singleton
    - Read-only lookup of the mentee-notes document (404 if missing)
    """

    @classmethod
    def _collection_name(cls, config):
        """Resolve the Mentee collection name from shared config."""
        return config.MENTEE_COLLECTION_NAME

    @classmethod
    def _check_permission(cls, token, operation):
        """
        Authorize an operation for the Mentee domain.

        Users granted either the ``mentor`` or ``admin`` role (per the shared
        ``Config`` role constants) may access mentee data through this service.

        Args:
            token: Token dictionary with user_id and roles
            operation: The operation being performed (e.g., 'read')

        Raises:
            HTTPForbidden: If the caller holds neither the ``mentor`` nor the
                ``admin`` role
        """
        config = Config.get_instance()
        allowed_roles = {config.ROLE_MENTOR, config.ROLE_ADMIN}
        roles = token.get("roles", []) or []
        if not allowed_roles.intersection(roles):
            raise HTTPForbidden("Mentor or admin role required to access mentee data")

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
        document exists; create-if-missing belongs on the Mentor API subclass.

        Args:
            profile_id: The mentee Profile id (string ObjectId)
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for audit/logging

        Returns:
            dict: The existing Mentee document

        Raises:
            HTTPBadRequest: If profile_id is not a valid ObjectId
            HTTPForbidden: If the caller does not hold the ``mentor`` role
            HTTPNotFound: If no Mentee document exists for the profile
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
            if existing:
                logger.info(
                    f"Retrieved mentee for profile {profile_id} "
                    f"for user {token.get('user_id')}"
                )
                return existing[0]

            raise HTTPNotFound(f"Mentee for profile {profile_id} not found")
        except (HTTPBadRequest, HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error retrieving mentee for profile {profile_id}: {str(e)}")
            raise HTTPInternalServerError(
                f"Failed to retrieve mentee for profile {profile_id}"
            )
