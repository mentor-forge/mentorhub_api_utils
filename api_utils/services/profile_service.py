"""
Profile service for business logic and RBAC.

Customer **controls** Profile and Admin **creates** Profile; every other domain
**consumes** it. This shared class therefore exposes only the consume surface
(get-by-token, get-by-id, paginated list) plus the global ``create_profile``
POST. Mentor Dashboard enrich lives on the Mentor API subclass, not here.

Per the API standards (separation of concerns), this service contains business
logic only. It raises the appropriate domain exceptions (e.g. HTTPForbidden,
HTTPNotFound); the route layer's ``@handle_route_exceptions`` wrapper is
responsible for translating those, and any unexpected error, into HTTP
responses.
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
from api_utils.flask_utils.exceptions import HTTPNotFound
import logging

logger = logging.getLogger(__name__)

# Live BSON schema (Profile 0.1.0.0): `_id`, `customer_id`, and `mentor_id` are
# objectId; the nested `experience[].roles[]` `start` / `end` fields are dates.
# Breadcrumb `at_time` values already arrive as datetime.
ID_PROPERTIES = ["_id", "customer_id", "mentor_id"]
DATE_PROPERTIES = ["start", "end"]

SYSTEM_MANAGED_FIELDS = ("_id", "created", "saved")

PROFILE_LIST_FILTERS = {
    "name": {"type": "contains", "field": "name"},
    "full_name": {"type": "contains", "field": "full_name"},
    "email": {"type": "contains", "field": "email"},
    "description": {"type": "contains", "field": "description"},
    "status": {"type": "in_list", "field": "status"},
    "roles": {"type": "in_list", "field": "roles"},
}

PROFILE_LIST_ORDER = {
    "default": {"field": "name", "order": "asc"},
    "allowed": {
        "name": ("asc", "desc"),
        "full_name": ("asc", "desc"),
        "email": ("asc", "desc"),
        "status": ("asc", "desc"),
        "created.at_time": ("asc", "desc"),
        "saved.at_time": ("asc", "desc"),
    },
}


class ProfileService:
    """
    Service class for Profile domain operations.

    Handles:
    - RBAC authorization checks
    - MongoDB operations via MongoIO singleton
    - Consume (GET / list) and global create for the Profile domain
    """

    @classmethod
    def _check_permission(cls, token, operation):
        """
        Check if the user has permission to perform an operation.

        Args:
            token: Token dictionary with user_id and roles
            operation: The operation being performed (e.g., 'read', 'create')

        Raises:
            HTTPForbidden: If user doesn't have required permission

        Reads and creates on the shared class require a valid token only.
        Admin and Customer subclasses add the inbound write check for
        ``create_profile``; outbound read filtering arrives in R082.
        """
        pass

    @classmethod
    def get_profile_by_token(cls, token, breadcrumb):
        """
        Resolve the caller's Profile from the JWT identity.

        Per the domain convention, the caller's Profile is the one whose
        ``name`` matches the token's ``user_id``. This is the canonical
        service-to-service entry point other services use to resolve the
        caller's Profile (e.g. the mentor id stored as ``Encounter.mentor_id``)
        without reaching into the Profile collection themselves.

        Args:
            token: Token dictionary with ``user_id`` and roles
            breadcrumb: Breadcrumb dictionary for audit/logging

        Returns:
            dict | None: The caller's Profile document, or ``None`` if no
            Profile matches the token identity.
        """
        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        profiles = mongo.get_documents(
            config.PROFILE_COLLECTION_NAME,
            match={"name": token.get("user_id")},
        )
        return profiles[0] if profiles else None

    @classmethod
    def get_profiles(
        cls,
        token,
        breadcrumb,
        offset=DEFAULT_OFFSET,
        size=DEFAULT_SIZE,
        filters=None,
        sort_by=None,
    ):
        """
        Get a paginated array of profile documents.

        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            offset: Zero-based start index
            size: Number of documents to return
            filters: Parsed filter dict from parse_filter_params
            sort_by: PyMongo sort list from build_sort_by; default name asc

        Returns:
            list: Profile documents
        """
        cls._check_permission(token, "read")

        config = Config.get_instance()
        # Outbound RBAC scoping (archived rows, customer/mentor/own-profile
        # visibility) lands in R082; until then the list is unscoped.
        base_match = {}
        match = build_match_filter(base_match, filters or {}, PROFILE_LIST_FILTERS)
        if sort_by is None:
            default = PROFILE_LIST_ORDER["default"]
            sort_by = build_sort_by(
                default["field"], default["order"], PROFILE_LIST_ORDER
            )

        profiles = execute_list_query(
            config.PROFILE_COLLECTION_NAME,
            match=match,
            sort_by=sort_by,
            offset=offset,
            size=size,
        )

        logger.info(
            f"Retrieved {len(profiles)} profiles (offset={offset}, size={size}) "
            f"for user {token.get('user_id')}"
        )
        return profiles

    @classmethod
    def get_profile(cls, profile_id, token, breadcrumb):
        """
        Retrieve a single profile document by ID.

        Args:
            profile_id: The Profile ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The Profile document

        Raises:
            HTTPNotFound: If the Profile is not found
        """
        cls._check_permission(token, "read")

        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        profile = mongo.get_document(config.PROFILE_COLLECTION_NAME, profile_id)
        if profile is None:
            raise HTTPNotFound(f"Profile {profile_id} not found")

        logger.info(f"Retrieved profile {profile_id} for user {token.get('user_id')}")
        return profile

    @classmethod
    def create_profile(cls, data, token, breadcrumb):
        """
        Create a new profile document.

        Args:
            data: Dictionary containing profile data
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The created profile document including _id
        """
        cls._check_permission(token, "create")

        for field in SYSTEM_MANAGED_FIELDS:
            data.pop(field, None)

        encode_document(data, ID_PROPERTIES, DATE_PROPERTIES)

        data["created"] = breadcrumb
        data["saved"] = breadcrumb

        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        profile_id = mongo.create_document(config.PROFILE_COLLECTION_NAME, data)
        if "_id" not in data:
            data["_id"] = ObjectId(profile_id)

        logger.info(f"Created profile {profile_id} for user {token.get('user_id')}")
        return data
