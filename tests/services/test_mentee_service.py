"""
Unit tests for Mentee service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from api_utils.services.mentee_service import MenteeService
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPNotFound,
    HTTPInternalServerError,
)

PROFILE_ID = "507f1f77bcf86cd799439011"
MENTOR_ID = ObjectId("507f1f77bcf86cd799439001")
OTHER_PROFILE_ID = "507f1f77bcf86cd799439099"
MENTEE_ID = "507f1f77bcf86cd7994390aa"


def _make_config():
    return MagicMock(
        spec=["MENTEE_COLLECTION_NAME", "PROFILE_COLLECTION_NAME", "ROLE_ADMIN"],
        MENTEE_COLLECTION_NAME="Mentee",
        PROFILE_COLLECTION_NAME="Profile",
        ROLE_ADMIN="admin",
    )


def _mentor_token():
    return {
        "user_id": "mike",
        "roles": ["mentor"],
        "profile_id": str(MENTOR_ID),
        "mentor_id": str(MENTOR_ID),
    }


class TestMenteeService(unittest.TestCase):
    """Test cases for MenteeService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = _mentor_token()
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "mike",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.mentee_service.Config.get_instance")
    @patch("api_utils.services.mentee_service.MongoIO.get_instance")
    def test_get_mentee_existing(self, mock_get_mongo, mock_get_config):
        """get_mentee returns the existing document when the mentor may see it."""
        mock_get_config.return_value = _make_config()

        existing = {
            "_id": ObjectId(MENTEE_ID),
            "profile_id": ObjectId(PROFILE_ID),
            "status": "active",
        }
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [existing]
        mock_mongo.get_document.return_value = {
            "_id": ObjectId(PROFILE_ID),
            "mentor_id": MENTOR_ID,
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = MenteeService.get_mentee(
            PROFILE_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, existing)
        mock_mongo.get_documents.assert_called_once_with(
            "Mentee", match={"profile_id": ObjectId(PROFILE_ID)}
        )

    @patch("api_utils.services.mentee_service.Config.get_instance")
    @patch("api_utils.services.mentee_service.MongoIO.get_instance")
    def test_get_mentee_not_found_when_missing(self, mock_get_mongo, mock_get_config):
        """get_mentee raises HTTPNotFound when no document exists."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound) as context:
            MenteeService.get_mentee(PROFILE_ID, self.mock_token, self.mock_breadcrumb)

        self.assertIn(PROFILE_ID, str(context.exception))

    @patch("api_utils.services.mentee_service.Config.get_instance")
    @patch("api_utils.services.mentee_service.MongoIO.get_instance")
    def test_get_mentee_hidden_for_unrelated_caller(
        self, mock_get_mongo, mock_get_config
    ):
        """get_mentee raises HTTPNotFound when the document is out of scope."""
        mock_get_config.return_value = _make_config()

        existing = {
            "_id": ObjectId(MENTEE_ID),
            "profile_id": ObjectId(OTHER_PROFILE_ID),
            "status": "active",
        }
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [existing]
        mock_mongo.get_document.return_value = {
            "_id": ObjectId(OTHER_PROFILE_ID),
            "mentor_id": ObjectId("507f1f77bcf86cd799439088"),
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            MenteeService.get_mentee(
                OTHER_PROFILE_ID, self.mock_token, self.mock_breadcrumb
            )

    @patch("api_utils.services.mentee_service.Config.get_instance")
    @patch("api_utils.services.mentee_service.MongoIO.get_instance")
    def test_get_mentee_own_profile(self, mock_get_mongo, mock_get_config):
        """A mentee may read their own mentee-notes document."""
        mock_get_config.return_value = _make_config()

        existing = {
            "_id": ObjectId(MENTEE_ID),
            "profile_id": ObjectId(PROFILE_ID),
            "status": "active",
        }
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [existing]
        mock_get_mongo.return_value = mock_mongo

        token = {
            "user_id": "daniel",
            "roles": ["mentee"],
            "profile_id": PROFILE_ID,
        }
        result = MenteeService.get_mentee(PROFILE_ID, token, self.mock_breadcrumb)

        self.assertEqual(result, existing)

    @patch("api_utils.services.mentee_service.Config.get_instance")
    @patch("api_utils.services.mentee_service.MongoIO.get_instance")
    def test_get_mentee_invalid_profile_id(self, mock_get_mongo, mock_get_config):
        """get_mentee raises HTTPBadRequest for an invalid profile_id."""
        mock_get_config.return_value = _make_config()
        mock_mongo = MagicMock()
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPBadRequest):
            MenteeService.get_mentee(
                "not-an-objectid", self.mock_token, self.mock_breadcrumb
            )
        mock_mongo.get_documents.assert_not_called()

    @patch("api_utils.services.mentee_service.Config.get_instance")
    @patch("api_utils.services.mentee_service.MongoIO.get_instance")
    def test_get_mentee_handles_exception(self, mock_get_mongo, mock_get_config):
        """get_mentee wraps unexpected database errors as HTTPInternalServerError."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            MenteeService.get_mentee(PROFILE_ID, self.mock_token, self.mock_breadcrumb)

    @patch("api_utils.services.mentee_service.Config.get_instance")
    def test_check_permission_requires_token_only(self, mock_get_config):
        """Shared reads require a valid token; outbound filtering is separate."""
        mock_get_config.return_value = _make_config()
        MenteeService._check_permission({"user_id": "carol", "roles": []}, "read")

    def test_collection_name_uses_config(self):
        """The collection name is read from Config.MENTEE_COLLECTION_NAME."""
        config = MagicMock()
        config.MENTEE_COLLECTION_NAME = "MenteeCustom"
        self.assertEqual(MenteeService._collection_name(config), "MenteeCustom")


if __name__ == "__main__":
    unittest.main()
