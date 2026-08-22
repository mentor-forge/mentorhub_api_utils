"""
ExternalEvent service for append-only ingress writes.

Handles RBAC checks and MongoDB operations for ExternalEvent domain.
"""

from bson import ObjectId

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.flask_utils.exceptions import (
    HTTPForbidden,
    HTTPInternalServerError,
)
import logging

logger = logging.getLogger(__name__)

# Live BSON schema (ExternalEvent 0.1.0.0): only `_id` is objectId.
# `external_id` is a provider message string, not ObjectId.
# `created.at_time` is a date; breadcrumbs already supply datetime.
ID_PROPERTIES = ["_id"]
DATE_PROPERTIES = []


class ExternalEventService:
    """
    Service class for ExternalEvent domain operations (append-only).
    """

    @staticmethod
    def _check_permission(token, operation):
        """Any authenticated user may create external events."""
        pass

    @staticmethod
    def create_external_event(data, token, breadcrumb):
        """
        Create a new external event document.

        Args:
            data: Dictionary containing external event data
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The created external event document including _id
        """
        try:
            ExternalEventService._check_permission(token, "create")

            if "_id" in data:
                del data["_id"]
            data.pop("created", None)

            encode_document(data, ID_PROPERTIES, DATE_PROPERTIES)

            data["created"] = breadcrumb

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            event_id = mongo.create_document(
                config.EXTERNAL_EVENT_COLLECTION_NAME, data
            )
            if "_id" not in data:
                data["_id"] = ObjectId(event_id)
            logger.info(
                f"Created external event {event_id} for user {token.get('user_id')}"
            )

            return data
        except HTTPForbidden:
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating external event: {error_msg}")
            raise HTTPInternalServerError(
                f"Failed to create external event: {error_msg}"
            )
