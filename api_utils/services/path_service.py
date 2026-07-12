"""
Path service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Path domain.
"""

from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPForbidden,
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
    Service class for Path domain operations.

    Handles:
    - RBAC authorization checks (placeholder for future implementation)
    - MongoDB operations via MongoIO singleton
    - Business logic for Path domain (read-only)
    """

    @staticmethod
    def _check_permission(token, operation):
        """
        Check if the user has permission to perform an operation.

        Args:
            token: Token dictionary with user_id and roles
            operation: The operation being performed (e.g., 'read')

        Raises:
            HTTPForbidden: If user doesn't have required permission

        Note: This is a placeholder for future RBAC implementation.
        For now, all operations require a valid token (authentication only).
        """
        pass

    @staticmethod
    def _collect_resource_ids(path):
        resource_ids = []
        seen = set()
        for module in path.get("modules") or []:
            for topic in module.get("topics") or []:
                for resource_id in topic.get("resources") or []:
                    resource_key = str(resource_id)
                    if resource_key not in seen:
                        seen.add(resource_key)
                        resource_ids.append(resource_key)
        return resource_ids

    @staticmethod
    def _enrich_path_resources(path, resource_summaries):
        summary_by_id = {str(summary["_id"]): summary for summary in resource_summaries}
        enriched = dict(path)
        modules = []
        for module in path.get("modules") or []:
            enriched_module = dict(module)
            topics = []
            for topic in module.get("topics") or []:
                enriched_topic = dict(topic)
                enriched_resources = []
                for resource_id in topic.get("resources") or []:
                    summary = summary_by_id.get(str(resource_id))
                    if summary is not None:
                        enriched_resources.append(summary)
                enriched_topic["resources"] = enriched_resources
                topics.append(enriched_topic)
            enriched_module["topics"] = topics
            modules.append(enriched_module)
        enriched["modules"] = modules
        return enriched

    @staticmethod
    def get_paths(
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
            PathService._check_permission(token, "read")
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

    @staticmethod
    def get_path(path_id, token, breadcrumb):
        """
        Retrieve a specific path document by ID with enriched resource summaries.

        Args:
            path_id: The path ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The path document with enriched nested resources

        Raises:
            HTTPNotFound: If path is not found
        """
        try:
            PathService._check_permission(token, "read")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            path = mongo.get_document(config.PATH_COLLECTION_NAME, path_id)
            if path is None:
                raise HTTPNotFound(f"Path { path_id} not found")

            from api_utils.services.resource_service import ResourceService

            resource_ids = PathService._collect_resource_ids(path)
            resource_summaries = ResourceService.get_resources_by_ids(
                resource_ids, token, breadcrumb
            )
            enriched_path = PathService._enrich_path_resources(path, resource_summaries)

            logger.info(f"Retrieved path { path_id} for user {token.get('user_id')}")
            return enriched_path
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving path { path_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve path { path_id}")
