"""
Notification service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Notification domain.
"""

from bson import ObjectId

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_sort_by,
    execute_list_query,
)
from api_utils.flask_utils.exceptions import (
    HTTPForbidden,
    HTTPInternalServerError,
    HTTPNotFound,
)
import logging

logger = logging.getLogger(__name__)

# Live BSON schema (Notification 0.1.0.0): `_id`, `profile_id`, `customer_id`,
# and `mentor_id` are objectId. Breadcrumb `at_time` fields are dates;
# breadcrumbs already supply datetime. There is no `saved` field.
ID_PROPERTIES = ["_id", "profile_id", "customer_id", "mentor_id"]
DATE_PROPERTIES = []

NOTIFICATION_LIST_ORDER = {
    "default": {"field": "created.at_time", "order": "desc"},
    "allowed": {
        "created.at_time": ("asc", "desc"),
    },
}

SYSTEM_MANAGED_FIELDS = ("_id", "created", "dismissed", "cancelled", "saved")


class NotificationService:
    """
    Service class for Notification domain operations.
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """Any authenticated user may create, read, and dismiss notifications."""
        pass

    @classmethod
    def create_notification(cls, data, token, breadcrumb):
        """
        Create a new notification document.

        Args:
            data: Dictionary containing notification data
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The created notification document including _id
        """
        try:
            cls._check_permission(token, "create")

            for field in SYSTEM_MANAGED_FIELDS:
                data.pop(field, None)

            encode_document(data, ID_PROPERTIES, DATE_PROPERTIES)

            data["created"] = breadcrumb

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            notification_id = mongo.create_document(
                config.NOTIFICATION_COLLECTION_NAME, data
            )
            if "_id" not in data:
                data["_id"] = ObjectId(notification_id)
            logger.info(
                f"Created notification {notification_id} for user {token.get('user_id')}"
            )

            return data
        except HTTPForbidden:
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating notification: {error_msg}")
            raise HTTPInternalServerError(f"Failed to create notification: {error_msg}")

    @classmethod
    def get_notifications(
        cls,
        token,
        breadcrumb,
        *,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        match=None,
    ):
        """
        Get a paginated array of notification documents.

        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            offset: Zero-based start index
            size: Number of documents to return
            match: Optional MongoDB match filter callers can extend later

        Returns:
            list: Notification documents newest first by created.at_time
        """
        try:
            cls._check_permission(token, "read")

            config = Config.get_instance()
            list_match = dict(match) if match else {}
            if list_match:
                encode_document(list_match, ID_PROPERTIES, DATE_PROPERTIES)

            default = NOTIFICATION_LIST_ORDER["default"]
            sort_by = build_sort_by(
                default["field"], default["order"], NOTIFICATION_LIST_ORDER
            )

            notifications = execute_list_query(
                config.NOTIFICATION_COLLECTION_NAME,
                match=list_match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )

            logger.info(
                f"Retrieved {len(notifications)} notifications "
                f"(offset={offset}, size={size}) for user {token.get('user_id')}"
            )
            return notifications
        except Exception as e:
            logger.error(f"Error retrieving notifications: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve notifications")

    @classmethod
    def dismiss_notification(cls, notification_id, token, breadcrumb):
        """
        Set the dismissed breadcrumb on a notification document.

        Args:
            notification_id: The notification ID to dismiss
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary written to dismissed

        Returns:
            dict: The updated notification document

        Raises:
            HTTPNotFound: If the notification is not found
        """
        try:
            cls._check_permission(token, "update")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            updated = mongo.update_document(
                config.NOTIFICATION_COLLECTION_NAME,
                document_id=notification_id,
                set_data={"dismissed": breadcrumb},
            )

            if updated is None:
                raise HTTPNotFound(f"Notification {notification_id} not found")

            logger.info(
                f"Dismissed notification {notification_id} "
                f"for user {token.get('user_id')}"
            )
            return updated
        except (HTTPForbidden, HTTPNotFound):
            raise
        except Exception as e:
            logger.error(f"Error dismissing notification {notification_id}: {str(e)}")
            raise HTTPInternalServerError(
                f"Failed to dismiss notification {notification_id}"
            )
