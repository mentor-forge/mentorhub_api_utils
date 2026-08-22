"""
Resource service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Resource domain.
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
    and_match,
    build_match_filter,
    build_sort_by,
    execute_list_query,
)
from api_utils.services.rbac import build_outbound_match, require_outbound
import logging

from bson import ObjectId

logger = logging.getLogger(__name__)

ARCHIVED_STATUS = "archived"

RESOURCE_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "description": {"type": "contains", "field": "description"},
    "status": {"type": "in_list", "field": "status"},
    "url": {"type": "contains", "field": "url"},
    "interests": {"type": "in_list", "field": "interests"},
    "technologies": {"type": "in_list", "field": "technologies"},
    "skill_level": {"type": "in_list", "field": "skill_level"},
}

RESOURCE_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {
        "name": ("asc", "desc"),
        "description": ("asc", "desc"),
        "status": ("asc", "desc"),
        "created.at_time": ("asc", "desc"),
        "saved.at_time": ("asc", "desc"),
    },
}


class ResourceService:
    """
    Service class for Resource domain operations.

    Handles:
    - Outbound RBAC visibility on shared GET/list
    - MongoDB operations via MongoIO singleton
    - Business logic for Resource domain (read-only)
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """Shared reads require a valid token only; outbound filtering applies separately."""
        pass

    @classmethod
    def _outbound_match(cls, token):
        """Catalog consume: non-admin callers see non-archived resources only."""
        return build_outbound_match(token, [{"status": {"$ne": ARCHIVED_STATUS}}])

    @classmethod
    def get_resources(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Get a paginated array of resource documents.

        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            offset: Zero-based start index
            size: Number of documents to return
            filters: Parsed filter dict from parse_filter_params
            sort_by: PyMongo sort list from build_sort_by; default name asc

        Returns:
            list: Resource documents

        Raises:
            HTTPBadRequest: If invalid parameters provided
        """
        try:
            cls._check_permission(token, "read")

            config = Config.get_instance()
            match = build_match_filter(
                cls._outbound_match(token), filters or {}, RESOURCE_LIST_FILTERS
            )
            if sort_by is None:
                default = RESOURCE_LIST_ORDER["default"]
                sort_by = build_sort_by(
                    default["field"], default["order"], RESOURCE_LIST_ORDER
                )

            resources = execute_list_query(
                config.RESOURCE_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )

            logger.info(
                f"Retrieved {len(resources)} resources (offset={offset}, size={size}) "
                f"for user {token.get('user_id')}"
            )
            return resources
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving resources: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve resources")

    @classmethod
    def _to_resource_summary(cls, resource):
        return {
            "_id": str(resource["_id"]),
            "name": resource.get("name"),
            "description": resource.get("description"),
        }

    @classmethod
    def get_resources_by_ids(cls, resource_ids, token, breadcrumb):
        """
        Get minimal Resource summaries for a list of Resource IDs.

        Args:
            resource_ids: Resource ID strings to look up
            token: Authentication token
            breadcrumb: Audit breadcrumb

        Returns:
            list: Minimal resource dicts with _id, name, and description
        """
        try:
            cls._check_permission(token, "read")

            unique_ids = []
            seen = set()
            for resource_id in resource_ids or []:
                resource_key = str(resource_id)
                if resource_key not in seen:
                    seen.add(resource_key)
                    unique_ids.append(resource_key)

            if not unique_ids:
                return []

            object_ids = []
            for resource_id in unique_ids:
                try:
                    object_ids.append(ObjectId(resource_id))
                except Exception:
                    continue

            if not object_ids:
                return []

            mongo = MongoIO.get_instance()
            config = Config.get_instance()

            query = and_match(
                {"_id": {"$in": object_ids}},
                cls._outbound_match(token),
            )

            documents = mongo.get_documents(
                config.RESOURCE_COLLECTION_NAME,
                match=query,
                project={"name": 1, "description": 1},
            )

            summaries = [cls._to_resource_summary(resource) for resource in documents]

            logger.info(
                f"Retrieved {len(summaries)} resource summaries "
                f"for user {token.get('user_id')}"
            )
            return summaries
        except Exception as e:
            logger.error(f"Error retrieving resources by ids: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve resources by ids")

    @classmethod
    def get_resource(cls, resource_id, token, breadcrumb):
        """
        Retrieve a specific resource document by ID.

        Args:
            resource_id: The resource ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The resource document

        Raises:
            HTTPNotFound: If resource is not found or not visible
        """
        try:
            cls._check_permission(token, "read")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            resource = mongo.get_document(config.RESOURCE_COLLECTION_NAME, resource_id)
            require_outbound(
                resource,
                cls._outbound_match(token),
                not_found_message=f"Resource {resource_id} not found",
            )

            logger.info(
                f"Retrieved resource { resource_id} for user {token.get('user_id')}"
            )
            return resource
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving resource { resource_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve resource { resource_id}")
