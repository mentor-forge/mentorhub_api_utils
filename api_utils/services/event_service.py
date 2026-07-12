"""
Event service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Event domain.
"""

from bson import ObjectId

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_match_filter,
    build_sort_by,
    execute_list_query,
)
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
    HTTPInternalServerError,
)
import logging

logger = logging.getLogger(__name__)

ID_PROPERTIES = ["_id", "profile_id", "resource_id", "journey_id"]
DATE_PROPERTIES = []

EVENT_LIST_FILTERS = {
    "type": {"type": "in_list", "field": "type"},
}

EVENT_LIST_ORDER = {
    "default": {"field": "created.at_time", "order": "desc"},
    "allowed": {
        "type": ("asc", "desc"),
        "created.at_time": ("asc", "desc"),
    },
}


class EventService:
    """
    Service class for Event domain operations.
    """

    @staticmethod
    def _check_permission(token, operation):
        """Any authenticated user may create and read events."""
        pass

    @staticmethod
    def create_event(data, token, breadcrumb):
        """
        Create a new event document.

        Args:
            data: Dictionary containing event data (type only from client)
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The created event document including _id
        """
        try:
            EventService._check_permission(token, "create")

            if "_id" in data:
                del data["_id"]
            data.pop("context", None)
            data.pop("created", None)

            data["context"] = dict(token)

            encode_document(data, ID_PROPERTIES, DATE_PROPERTIES)

            data["created"] = breadcrumb

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            event_id = mongo.create_document(config.EVENT_COLLECTION_NAME, data)
            if "_id" not in data:
                data["_id"] = ObjectId(event_id)
            logger.info(f"Created event {event_id} for user {token.get('user_id')}")

            if data.get("type") == config.EVENT_TYPE_LINK:
                resource_id = token.get("resource_id")
                if resource_id:
                    from api_utils.services.aggregation_service import (
                        AggregationService,
                    )

                    AggregationService.add_hit(resource_id, token, breadcrumb)
                else:
                    logger.warning(
                        "link event created without resource_id in token; skipping add_hit"
                    )

            return data
        except HTTPForbidden:
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating event: {error_msg}")
            raise HTTPInternalServerError(f"Failed to create event: {error_msg}")

    @staticmethod
    def get_events(
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
        *,
        profile_id=None,
    ):
        """
        Get a paginated array of event documents.

        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            offset: Zero-based start index
            size: Number of documents to return
            filters: Parsed filter dict (optional type in_list)
            sort_by: PyMongo sort list; default created.at_time desc
            profile_id: Optional scope on context.profile_id

        Returns:
            list: Event documents
        """
        try:
            EventService._check_permission(token, "read")

            config = Config.get_instance()
            base_match = {}
            if profile_id is not None:
                from bson.errors import InvalidId

                try:
                    base_match["context.profile_id"] = ObjectId(profile_id)
                except (InvalidId, TypeError):
                    raise HTTPBadRequest(
                        "profile_id must be a valid MongoDB ObjectId"
                    )

            match = build_match_filter(base_match, filters or {}, EVENT_LIST_FILTERS)
            if sort_by is None:
                default = EVENT_LIST_ORDER["default"]
                sort_by = build_sort_by(
                    default["field"], default["order"], EVENT_LIST_ORDER
                )

            events = execute_list_query(
                config.EVENT_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )

            logger.info(
                f"Retrieved {len(events)} events (offset={offset}, size={size}) "
                f"for user {token.get('user_id')}"
            )
            return events
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving events: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve events")
