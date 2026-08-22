"""
Unit tests for the shared Profile service.

The shared class is consume-only plus the global ``create_profile`` POST:
get-by-token, plain get-by-id, and a paginated list. Mentor Dashboard enrich
lives on the Mentor API subclass and is not exercised here. Outbound RBAC
filtering (archived rows, customer/mentor scope) arrives in R082, so these
tests assert an unscoped base match.
"""

import copy
import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from api_utils.services.profile_service import ProfileService
from api_utils.flask_utils.exceptions import HTTPNotFound

MENTOR_ID = ObjectId("507f1f77bcf86cd799439001")
MENTEE_1_ID = ObjectId("507f1f77bcf86cd799439011")
MENTEE_2_ID = ObjectId("507f1f77bcf86cd799439012")
CUSTOMER_ID = ObjectId("507f1f77bcf86cd7994390cc")
NEW_PROFILE_ID = ObjectId("507f1f77bcf86cd7994390dd")


def _make_config():
    mock_config = MagicMock()
    mock_config.PROFILE_COLLECTION_NAME = "Profile"
    mock_config.ROLE_MENTOR = "mentor"
    mock_config.ROLE_ADMIN = "admin"
    return mock_config


def _capture_create(mock_mongo, new_id):
    """Snapshot the document handed to MongoIO before the service stamps _id.

    The service mutates the same dict it passed in, so call_args would
    otherwise show the post-insert state.
    """
    captured = {}

    def create_document(collection_name, document):
        captured["collection_name"] = collection_name
        captured["document"] = copy.deepcopy(document)
        return str(new_id)

    mock_mongo.create_document.side_effect = create_document
    return captured


class TestProfileService(unittest.TestCase):
    """Test cases for ProfileService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {"user_id": "mike", "roles": ["mentor"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "mike",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_by_token_returns_caller_profile(
        self, mock_get_mongo, mock_get_config
    ):
        """The caller's Profile is the one whose name matches token user_id."""
        mock_get_config.return_value = _make_config()

        profile_doc = {"_id": MENTOR_ID, "name": "mike"}
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [profile_doc]
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.get_profile_by_token(
            self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, profile_doc)
        mock_mongo.get_documents.assert_called_once_with(
            "Profile", match={"name": "mike"}
        )

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_by_token_returns_none_when_missing(
        self, mock_get_mongo, mock_get_config
    ):
        """A token with no matching Profile resolves to None, not an error."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.get_profile_by_token(
            {"user_id": "nobody", "roles": []}, self.mock_breadcrumb
        )

        self.assertIsNone(result)

    @patch("api_utils.services.profile_service.execute_list_query")
    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profiles_returns_paginated_documents(
        self, mock_get_mongo, mock_get_config, mock_execute_list_query
    ):
        """The list is a plain page of documents sorted by name ascending."""
        mock_get_config.return_value = _make_config()
        mock_get_mongo.return_value = MagicMock()

        documents = [
            {"_id": MENTEE_1_ID, "name": "daniel"},
            {"_id": MENTEE_2_ID, "name": "lucky"},
        ]
        mock_execute_list_query.return_value = documents

        result = ProfileService.get_profiles(
            self.mock_token, self.mock_breadcrumb, offset=10, size=5
        )

        self.assertEqual(result, documents)
        mock_execute_list_query.assert_called_once_with(
            "Profile",
            match={},
            sort_by=[("name", 1), ("_id", 1)],
            offset=10,
            size=5,
        )

    @patch("api_utils.services.profile_service.execute_list_query")
    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profiles_applies_query_filters(
        self, mock_get_mongo, mock_get_config, mock_execute_list_query
    ):
        """Query filters AND into the match on top of an empty base match."""
        mock_get_config.return_value = _make_config()
        mock_get_mongo.return_value = MagicMock()
        mock_execute_list_query.return_value = []

        ProfileService.get_profiles(
            self.mock_token,
            self.mock_breadcrumb,
            filters={"name": "dan", "status": ["active", "provisioned"]},
        )

        match = mock_execute_list_query.call_args.kwargs["match"]
        self.assertEqual(
            match,
            {
                "name": {"$regex": "dan", "$options": "i"},
                "status": {"$in": ["active", "provisioned"]},
            },
        )

    @patch("api_utils.services.profile_service.execute_list_query")
    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profiles_allows_any_authenticated_role(
        self, mock_get_mongo, mock_get_config, mock_execute_list_query
    ):
        """Shared reads no longer demand the mentor or admin role."""
        mock_get_config.return_value = _make_config()
        mock_get_mongo.return_value = MagicMock()
        mock_execute_list_query.return_value = []

        result = ProfileService.get_profiles(
            {"user_id": "carol", "roles": ["coordinator"]}, self.mock_breadcrumb
        )

        self.assertEqual(result, [])

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_returns_plain_document(self, mock_get_mongo, mock_get_config):
        """get_profile returns the document itself, not a composite."""
        mock_get_config.return_value = _make_config()

        profile_doc = {"_id": MENTEE_1_ID, "name": "daniel"}
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = profile_doc
        mock_get_mongo.return_value = mock_mongo

        result = ProfileService.get_profile(
            str(MENTEE_1_ID), self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, profile_doc)
        mock_mongo.get_document.assert_called_once_with("Profile", str(MENTEE_1_ID))
        # No mentee/encounter composite means no cross-collection reads.
        mock_mongo.get_documents.assert_not_called()

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_not_found(self, mock_get_mongo, mock_get_config):
        """A missing Profile raises HTTPNotFound naming the requested id."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound) as context:
            ProfileService.get_profile("999", self.mock_token, self.mock_breadcrumb)
        self.assertIn("999", str(context.exception))

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_get_profile_propagates_unexpected_errors(
        self, mock_get_mongo, mock_get_config
    ):
        """Unexpected errors propagate untouched for the route wrapper to handle."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = RuntimeError("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(RuntimeError):
            ProfileService.get_profile("123", self.mock_token, self.mock_breadcrumb)

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_create_profile_stamps_breadcrumbs_and_encodes_ids(
        self, mock_get_mongo, mock_get_config
    ):
        """Create encodes id fields, stamps both breadcrumbs, and returns _id."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        captured = _capture_create(mock_mongo, NEW_PROFILE_ID)
        mock_get_mongo.return_value = mock_mongo

        data = {
            "name": "daniel",
            "full_name": "Daniel Mentee",
            "customer_id": str(CUSTOMER_ID),
            "mentor_id": str(MENTOR_ID),
            "status": "active",
        }

        result = ProfileService.create_profile(
            data, self.mock_token, self.mock_breadcrumb
        )

        # customer_id/mentor_id are objectId in the live BSON schema.
        stored = captured["document"]
        self.assertEqual(captured["collection_name"], "Profile")
        self.assertEqual(stored["customer_id"], CUSTOMER_ID)
        self.assertEqual(stored["mentor_id"], MENTOR_ID)
        self.assertEqual(stored["created"], self.mock_breadcrumb)
        self.assertEqual(stored["saved"], self.mock_breadcrumb)

        self.assertEqual(result["_id"], NEW_PROFILE_ID)
        self.assertEqual(result["name"], "daniel")

    @patch("api_utils.services.profile_service.Config.get_instance")
    @patch("api_utils.services.profile_service.MongoIO.get_instance")
    def test_create_profile_strips_system_managed_fields(
        self, mock_get_mongo, mock_get_config
    ):
        """Client-supplied _id, created, and saved are discarded."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        captured = _capture_create(mock_mongo, NEW_PROFILE_ID)
        mock_get_mongo.return_value = mock_mongo

        data = {
            "_id": str(MENTEE_1_ID),
            "name": "daniel",
            "created": {"by_user": "spoofed"},
            "saved": {"by_user": "spoofed"},
        }

        ProfileService.create_profile(data, self.mock_token, self.mock_breadcrumb)

        stored = captured["document"]
        self.assertNotIn("_id", stored)
        self.assertEqual(stored["created"], self.mock_breadcrumb)
        self.assertEqual(stored["saved"], self.mock_breadcrumb)

    @patch("api_utils.services.profile_service.Config.get_instance")
    def test_check_permission_is_authentication_only(self, mock_get_config):
        """Reads and creates on the shared class require only a valid token."""
        mock_get_config.return_value = _make_config()
        ProfileService._check_permission(
            {"user_id": "carol", "roles": ["coordinator"]}, "read"
        )
        ProfileService._check_permission({"user_id": "carol", "roles": []}, "create")

    def test_dashboard_enrich_is_not_on_the_shared_class(self):
        """Mentor Dashboard enrich moved to the Mentor API subclass."""
        for name in (
            "get_profile_properties",
            "_resource_ref",
            "_load_resource",
            "_mentor_history",
        ):
            self.assertFalse(
                hasattr(ProfileService, name),
                f"{name} should no longer exist on the shared ProfileService",
            )


if __name__ == "__main__":
    unittest.main()
