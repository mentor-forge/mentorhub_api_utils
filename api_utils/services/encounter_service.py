"""
Encounter service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Encounter domain.
"""

from api_utils import MongoIO, Config
from api_utils.mongo_utils import encode_document
from api_utils.mongo_utils.list_query import and_match
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)
from api_utils.services.rbac import (
    EMPTY_SCOPE_MATCH,
    build_outbound_match,
    require_outbound,
)
from bson import ObjectId
from bson.errors import InvalidId
from pymongo import DESCENDING
import logging

logger = logging.getLogger(__name__)

ARCHIVED_STATUS = "archived"
ENCOUNTER_ID_PROPERTIES = ["mentor_id", "mentee_id"]


class EncounterService:
    """
    Service class for Encounter domain operations (read-only in shared api_utils).

    Handles:
    - Outbound RBAC visibility on shared GET/list
    - MongoDB operations via MongoIO singleton
    """

    @classmethod
    def _check_permission(cls, token, operation, breadcrumb):
        """Shared reads require a valid token only; outbound filtering applies separately."""
        pass

    @classmethod
    def _encounter_identity_or(cls, token):
        or_clauses = []
        profile_id = token.get("profile_id")
        mentor_id = token.get("mentor_id")

        if mentor_id:
            clause = {"mentor_id": mentor_id}
            encode_document(clause, ENCOUNTER_ID_PROPERTIES, [])
            or_clauses.append(clause)
        if profile_id:
            mentor_clause = {"mentor_id": profile_id}
            encode_document(mentor_clause, ENCOUNTER_ID_PROPERTIES, [])
            or_clauses.append(mentor_clause)
            mentee_clause = {"mentee_id": profile_id}
            encode_document(mentee_clause, ENCOUNTER_ID_PROPERTIES, [])
            or_clauses.append(mentee_clause)

        if not or_clauses:
            return EMPTY_SCOPE_MATCH
        return {"$or": or_clauses}

    @classmethod
    def _outbound_match(cls, token):
        return build_outbound_match(
            token,
            [
                {"status": {"$ne": ARCHIVED_STATUS}},
                cls._encounter_identity_or(token),
            ],
        )

    @classmethod
    def _normalize_mentee_id(cls, mentee_id):
        """
        Normalize a mentee id for matching against ``Encounter.mentee_id``.

        Encounter documents store ``mentee_id`` as a BSON ``ObjectId`` (the
        mentee's Profile id). Callers may pass either an ``ObjectId`` (e.g. the
        dashboard, which already holds the mentee's ``_id``) or a string id
        (e.g. the detail route). A valid string id is converted so the direct
        Mongo match works; anything else is returned unchanged.
        """
        if isinstance(mentee_id, ObjectId):
            return mentee_id
        try:
            return ObjectId(mentee_id)
        except (InvalidId, TypeError):
            return mentee_id

    @classmethod
    def get_recent_encounter(cls, mentee_id, token, breadcrumb):
        """
        Return a summary of a mentee's most recent Encounter, or ``None``.

        The most recent encounter is the one with the latest ``date``. The
        summary mirrors the Mentor Dashboard card contract: ``_id``, ``date``,
        ``tldr``, and ``summary``.

        Args:
            mentee_id: The mentee Profile id whose latest encounter is wanted
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for audit/logging

        Returns:
            dict | None: The most recent encounter summary, or ``None`` when the
            mentee has no visible encounters.
        """
        cls._check_permission(token, "read", breadcrumb)

        mongo = MongoIO.get_instance()
        config = Config.get_instance()
        query = and_match(
            {"mentee_id": cls._normalize_mentee_id(mentee_id)},
            cls._outbound_match(token),
        )
        encounters = mongo.get_documents(
            config.ENCOUNTER_COLLECTION_NAME,
            match=query,
            sort_by=[("date", DESCENDING)],
        )
        if not encounters:
            return None

        encounter = encounters[0]
        return {
            "_id": encounter["_id"],
            "date": encounter.get("date"),
            "tldr": encounter.get("tldr"),
            "summary": encounter.get("summary"),
        }

    @classmethod
    def get_encounters_for_mentee(
        cls, mentee_id, token, breadcrumb, offset=None, size=None
    ):
        """
        Return a mentee's Encounter documents, most recent first.

        This is the dedicated per-mentee read used by the Profile detail
        composite. It queries the Encounter collection directly by
        ``mentee_id`` and sorts by ``date`` descending.

        Pagination is **optional** and scoped to the given ``mentee_id``: when
        both ``offset`` and ``size`` are provided the read is paged
        (``skip``/``limit``); when omitted (the default) the full list is
        returned so existing composite callers (``ProfileService.get_profile``
        and ``get_profile_properties``) are unaffected.

        Args:
            mentee_id: The mentee Profile id whose encounters are wanted
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for audit/logging
            offset: Optional zero-based start index (paginated read)
            size: Optional page size (paginated read)

        Returns:
            list[dict]: The mentee's visible Encounter documents, most recent first.
        """
        cls._check_permission(token, "read", breadcrumb)

        mongo = MongoIO.get_instance()
        config = Config.get_instance()

        query_kwargs = {
            "match": and_match(
                {"mentee_id": cls._normalize_mentee_id(mentee_id)},
                cls._outbound_match(token),
            ),
            "sort_by": [("date", DESCENDING)],
        }
        if offset is not None and size is not None:
            query_kwargs["skip"] = offset
            query_kwargs["limit"] = size

        encounters = mongo.get_documents(
            config.ENCOUNTER_COLLECTION_NAME,
            **query_kwargs,
        )
        logger.info(
            f"Retrieved {len(encounters)} encounters for mentee {mentee_id} "
            f"for user {token.get('user_id')}"
        )
        return encounters

    @classmethod
    def get_encounter(cls, encounter_id, token, breadcrumb):
        """
        Retrieve a specific encounter document by ID.

        Args:
            encounter_id: The encounter ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging

        Returns:
            dict: The encounter document

        Raises:
            HTTPNotFound: If encounter is not found or not visible
        """
        try:
            cls._check_permission(token, "read", breadcrumb)

            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            encounter = mongo.get_document(
                config.ENCOUNTER_COLLECTION_NAME, encounter_id
            )
            require_outbound(
                encounter,
                cls._outbound_match(token),
                not_found_message=f"Encounter {encounter_id} not found",
            )

            logger.info(
                f"Retrieved encounter { encounter_id} for user {token.get('user_id')}"
            )
            return encounter
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving encounter { encounter_id}: {str(e)}")
            raise HTTPInternalServerError(
                f"Failed to retrieve encounter { encounter_id}"
            )
