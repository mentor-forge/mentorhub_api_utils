"""
Note service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Note domain.
"""

from bson import ObjectId

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    MAX_SIZE,
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

ID_PROPERTIES = ["_id", "resource_id", "profile_id"]
DATE_PROPERTIES = []

NOTE_LIST_FILTERS = {
    "status": {"type": "in_list", "field": "status"},
}

NOTE_LIST_ORDER = {
    "default": {"field": "created.at_time", "order": "desc"},
    "allowed": {"created.at_time": ("asc", "desc")},
}


class NoteService:
    """
    Service class for Note domain operations.
    """

    @staticmethod
    def _check_permission(token, operation):
        """Any authenticated user may create and read notes."""
        pass

    @staticmethod
    def create_note(data, token, breadcrumb):
        """
        Create a new note document.

        Args:
            data: Dictionary containing note data
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The created note document including _id
        """
        try:
            NoteService._check_permission(token, "create")

            if "_id" in data:
                del data["_id"]

            encode_document(data, ID_PROPERTIES, DATE_PROPERTIES)

            data["created"] = breadcrumb
            data["saved"] = breadcrumb

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            note_id = mongo.create_document(config.NOTE_COLLECTION_NAME, data)
            if "_id" not in data:
                data["_id"] = ObjectId(note_id)
            logger.info(f"Created note {note_id} for user {token.get('user_id')}")
            return data
        except HTTPForbidden:
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating note: {error_msg}")
            raise HTTPInternalServerError(f"Failed to create note: {error_msg}")

    @staticmethod
    def get_notes_for_resource(
        resource_id,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Retrieve paginated notes for a resource.

        Args:
            resource_id: The resource ID to look up
            token: Authentication token
            breadcrumb: Audit breadcrumb
            offset: Zero-based start index
            size: Number of documents to return
            filters: Parsed filter dict (optional status in_list)
            sort_by: PyMongo sort list; default created.at_time desc

        Returns:
            list: Note documents for the resource
        """
        try:
            NoteService._check_permission(token, "read")

            from bson.errors import InvalidId

            try:
                resource_object_id = ObjectId(resource_id)
            except (InvalidId, TypeError):
                raise HTTPBadRequest("resource_id must be a valid MongoDB ObjectId")

            config = Config.get_instance()
            base_match = {"resource_id": resource_object_id}
            match = build_match_filter(base_match, filters or {}, NOTE_LIST_FILTERS)
            if sort_by is None:
                default = NOTE_LIST_ORDER["default"]
                sort_by = build_sort_by(
                    default["field"], default["order"], NOTE_LIST_ORDER
                )

            notes = execute_list_query(
                config.NOTE_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )

            logger.info(
                f"Retrieved {len(notes)} notes for resource {resource_id} "
                f"for user {token.get('user_id')}"
            )
            return notes
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving notes for resource {resource_id}: {str(e)}")
            raise HTTPInternalServerError(
                f"Failed to retrieve notes for resource {resource_id}"
            )

    @staticmethod
    def list_all_notes_for_resource(resource_id, token, breadcrumb):
        """Return all notes for a resource (composite/detail reads)."""
        return NoteService.get_notes_for_resource(
            resource_id,
            token,
            breadcrumb,
            offset=0,
            size=MAX_SIZE,
        )
