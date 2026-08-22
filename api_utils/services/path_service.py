"""
Path service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Path domain.
"""

from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.mongo_utils.list_query import (
    DEFAULT_OFFSET,
    DEFAULT_SIZE,
    build_match_filter,
    build_sort_by,
    execute_list_query,
)
import logging

logger = logging.getLogger(__name__)

PATH_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
}

PATH_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {"name": ("asc", "desc")},
}


class PathService:
    """
    Service class for Path domain operations (read-only in shared api_utils).

    Handles:
    - RBAC authorization checks (authenticated read)
    - MongoDB operations via MongoIO singleton
    - Raw Path document reads (resource enrich belongs on Mentee BFF)
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """Any authenticated user may read paths."""
        pass

    @classmethod
    def get_paths(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Get paginated path documents.

        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            offset: Zero-based start index
            size: Number of documents to return
            filters: Parsed filter dict (optional name contains)
            sort_by: PyMongo sort list; default name asc

        Returns:
            list: Path documents
        """
        try:
            cls._check_permission(token, "read")
            config = Config.get_instance()
            match = build_match_filter({}, filters or {}, PATH_LIST_FILTERS)
            if sort_by is None:
                default = PATH_LIST_ORDER["default"]
                sort_by = build_sort_by(
                    default["field"], default["order"], PATH_LIST_ORDER
                )

            paths = execute_list_query(
                config.PATH_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )
            logger.info(f"Retrieved {len(paths)} paths for user {token.get('user_id')}")
            return paths
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving paths: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve paths")

    @classmethod
    def get_path(cls, path_id, token, breadcrumb):
        """
        Retrieve a specific path document by ID (raw document; no resource enrich).

        Args:
            path_id: The path ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The path document

        Raises:
            HTTPNotFound: If path is not found
        """
        try:
            cls._check_permission(token, "read")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            path = mongo.get_document(config.PATH_COLLECTION_NAME, path_id)
            if path is None:
                raise HTTPNotFound(f"Path { path_id} not found")

            logger.info(f"Retrieved path { path_id} for user {token.get('user_id')}")
            return path
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving path { path_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve path { path_id}")
