"""
Plan service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Plan domain.
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

# Plan remains a mentor-only local domain, but adopts the shared header
# pagination + sort_by/order + filter conventions for list consistency.
PLAN_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
}

PLAN_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {"name": ("asc", "desc")},
}


class PlanService:
    """
    Service class for Plan domain operations (read-only in shared api_utils).

    Handles:
    - RBAC authorization checks (mentor-or-admin read)
    - MongoDB operations via MongoIO singleton
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """Authenticated read; mentor-or-admin enforced by controlling API routes."""
        pass

    @classmethod
    def get_plans(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Return a paginated array of plan documents.

        Plan is mentor-only and stays local, but the list adopts the shared
        conventions: ``offset``/``size`` pagination, ``sort_by``/``order``
        (default name asc), and an optional ``name`` contains filter. Returns a
        plain list; pagination metadata is conveyed via response headers by the
        route layer.
        """
        try:
            cls._check_permission(token, "read")
            config = Config.get_instance()

            match = build_match_filter({}, filters or {}, PLAN_LIST_FILTERS)
            if sort_by is None:
                default = PLAN_LIST_ORDER["default"]
                sort_by = build_sort_by(
                    default["field"], default["order"], PLAN_LIST_ORDER
                )

            plans = execute_list_query(
                config.PLAN_COLLECTION_NAME,
                match=match,
                sort_by=sort_by,
                offset=offset,
                size=size,
            )
            logger.info(f"Retrieved {len(plans)} plans for user {token.get('user_id')}")
            return plans
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving plans: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve plans")

    @classmethod
    def get_plan(cls, plan_id, token, breadcrumb):
        """
        Retrieve a specific plan document by ID.

        Args:
            plan_id: The plan ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The plan document

        Raises:
            HTTPNotFound: If plan is not found
        """
        try:
            cls._check_permission(token, "read")

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            plan = mongo.get_document(config.PLAN_COLLECTION_NAME, plan_id)
            if plan is None:
                raise HTTPNotFound(f"Plan { plan_id} not found")

            logger.info(f"Retrieved plan { plan_id} for user {token.get('user_id')}")
            return plan
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving plan { plan_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve plan { plan_id}")
