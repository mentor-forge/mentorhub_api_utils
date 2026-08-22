"""
Note service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Note domain.
"""

from bson import ObjectId

from api_utils import Config
from api_utils.mongo_utils import encode_document
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    MAX_SIZE,
    and_match,
    build_match_filter,
    build_sort_by,
    execute_list_query,
)
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
)
from api_utils.services.rbac import EMPTY_SCOPE_MATCH, build_outbound_match
import logging

logger = logging.getLogger(__name__)

ARCHIVED_STATUS = "archived"
NOTE_ID_PROPERTIES = ["profile_id"]

NOTE_LIST_FILTERS = {
    "status": {"type": "in_list", "field": "status"},
}

NOTE_LIST_ORDER = {
    "default": {"field": "created.at_time", "order": "desc"},
    "allowed": {"created.at_time": ("asc", "desc")},
}


class NoteService:
    """
    Service class for Note domain operations (read-only in shared api_utils).
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """Any authenticated user may read notes; outbound filtering applies separately."""
        pass

    @classmethod
    def _note_identity_or(cls, token):
        """Own-profile scope; Note schema has no customer_id field."""
        profile_id = token.get("profile_id")
        if not profile_id:
            return EMPTY_SCOPE_MATCH
        clause = {"profile_id": profile_id}
        encode_document(clause, NOTE_ID_PROPERTIES, [])
        return {"$or": [clause]}

    @classmethod
    def _outbound_match(cls, token):
        return build_outbound_match(
            token,
            [
                {"status": {"$ne": ARCHIVED_STATUS}},
                cls._note_identity_or(token),
            ],
        )

    @classmethod
    def get_notes_for_resource(
        cls,
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
            cls._check_permission(token, "read")

            from bson.errors import InvalidId

            try:
                resource_object_id = ObjectId(resource_id)
            except (InvalidId, TypeError):
                raise HTTPBadRequest("resource_id must be a valid MongoDB ObjectId")

            config = Config.get_instance()
            base_match = and_match(
                {"resource_id": resource_object_id},
                cls._outbound_match(token),
            )
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

    @classmethod
    def list_all_notes_for_resource(cls, resource_id, token, breadcrumb):
        """Return all notes for a resource (composite/detail reads)."""
        return cls.get_notes_for_resource(
            resource_id,
            token,
            breadcrumb,
            offset=0,
            size=MAX_SIZE,
        )
