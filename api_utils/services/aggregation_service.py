"""
Aggregation service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Resource_Aggregation domain.
"""

import logging

from bson import ObjectId
from bson.errors import InvalidId
from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
)
from api_utils.services.resource_service import ResourceService

logger = logging.getLogger(__name__)


class AggregationService:
    """
    Service class for Resource_Aggregation domain operations (read-only).
    """

    @classmethod
    def _resource_object_id(cls, resource_id):
        try:
            return ObjectId(resource_id)
        except (InvalidId, TypeError):
            raise HTTPBadRequest("resource_id must be a valid MongoDB ObjectId")

    @classmethod
    def _find_aggregation(cls, mongo, collection_name, resource_object_id):
        aggregation = mongo.get_document(collection_name, str(resource_object_id))
        if aggregation is not None:
            return aggregation

        legacy_matches = mongo.get_documents(
            collection_name, match={"resource_id": resource_object_id}
        )
        return legacy_matches[0] if legacy_matches else None

    @classmethod
    def get_aggregation_for_resource(cls, resource_id, token, breadcrumb):
        """
        Retrieve aggregation metrics for a resource.

        Returns:
            dict or None: The aggregation document, or None if none exists or the
            parent Resource is not visible to the caller
        """
        try:
            resource_object_id = cls._resource_object_id(resource_id)

            mongo = MongoIO.get_instance()
            config = Config.get_instance()

            resource = mongo.get_document(config.RESOURCE_COLLECTION_NAME, resource_id)
            from api_utils.services.rbac import matches_outbound

            if resource is None or not matches_outbound(
                resource, ResourceService._outbound_match(token)
            ):
                return None

            aggregation = cls._find_aggregation(
                mongo, config.RESOURCE_AGGREGATION_COLLECTION_NAME, resource_object_id
            )

            logger.info(
                f"Retrieved aggregation for resource {resource_id} "
                f"for user {token.get('user_id')}"
            )
            return aggregation
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(
                f"Error retrieving aggregation for resource {resource_id}: {str(e)}"
            )
            raise HTTPInternalServerError(
                f"Failed to retrieve aggregation for resource {resource_id}"
            )
