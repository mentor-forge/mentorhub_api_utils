"""
Unit tests for Encounter service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from pymongo import DESCENDING
from api_utils.services.encounter_service import EncounterService
from api_utils.flask_utils.exceptions import (
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)


def _make_config():
    """Build a config mock exposing the names/role constants the service reads."""
    mock_config = MagicMock()
    mock_config.ENCOUNTER_COLLECTION_NAME = "Encounter"
    mock_config.PROFILE_COLLECTION_NAME = "Profile"
    mock_config.ROLE_MENTOR = "mentor"
    mock_config.ROLE_ADMIN = "admin"
    return mock_config


class TestEncounterService(unittest.TestCase):
    """Test cases for EncounterService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of a specific encounter document."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "name": "encounter1",
        }
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_encounter(
            "123", self.mock_token, self.mock_breadcrumb
        )

        self.assertIsNotNone(result)
        self.assertEqual(result["_id"], "123")
        mock_mongo.get_document.assert_called_once_with("Encounter", "123")

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_not_found(self, mock_get_mongo, mock_get_config):
        """Test get_encounter raises HTTPNotFound when document not found."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound) as context:
            EncounterService.get_encounter("999", self.mock_token, self.mock_breadcrumb)
        self.assertIn("999", str(context.exception))

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_encounter handles database exceptions."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            EncounterService.get_encounter("123", self.mock_token, self.mock_breadcrumb)

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_recent_encounter_returns_summary(
        self, mock_get_mongo, mock_get_config
    ):
        """Most recent encounter is summarized for the dashboard card."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mentee_id = ObjectId("507f1f77bcf86cd799439011")
        encounter_id = ObjectId("507f1f77bcf86cd7994390aa")
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {
                "_id": encounter_id,
                "mentee_id": mentee_id,
                "date": "2025-02-01T00:00:00Z",
                "tldr": "great session",
                "summary": "covered async patterns",
                "notes": "extra field not returned in summary",
            }
        ]
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_recent_encounter(
            mentee_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(
            result,
            {
                "_id": encounter_id,
                "date": "2025-02-01T00:00:00Z",
                "tldr": "great session",
                "summary": "covered async patterns",
            },
        )

        mock_mongo.get_documents.assert_called_once()
        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(args[0], "Encounter")
        self.assertEqual(kwargs["match"], {"mentee_id": mentee_id})
        self.assertEqual(kwargs["sort_by"], [("date", DESCENDING)])

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_recent_encounter_none_when_no_encounters(
        self, mock_get_mongo, mock_get_config
    ):
        """Return None when the mentee has no encounters."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_recent_encounter(
            ObjectId("507f1f77bcf86cd799439011"),
            self.mock_token,
            self.mock_breadcrumb,
        )

        self.assertIsNone(result)

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounters_for_mentee_returns_sorted_list(
        self, mock_get_mongo, mock_get_config
    ):
        """All of a mentee's encounters are returned, most recent first."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        newer = {"_id": ObjectId("507f1f77bcf86cd7994390aa"), "date": "2025-03-01"}
        older = {"_id": ObjectId("507f1f77bcf86cd7994390a1"), "date": "2025-01-01"}
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [newer, older]
        mock_get_mongo.return_value = mock_mongo

        mentee_id = ObjectId("507f1f77bcf86cd799439011")
        result = EncounterService.get_encounters_for_mentee(
            mentee_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, [newer, older])
        mock_mongo.get_documents.assert_called_once()
        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(args[0], "Encounter")
        self.assertEqual(kwargs["match"], {"mentee_id": mentee_id})
        self.assertEqual(kwargs["sort_by"], [("date", DESCENDING)])

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounters_for_mentee_converts_string_id(
        self, mock_get_mongo, mock_get_config
    ):
        """A string mentee id is normalized to ObjectId for the direct query."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        mentee_id = "507f1f77bcf86cd799439011"
        EncounterService.get_encounters_for_mentee(
            mentee_id, self.mock_token, self.mock_breadcrumb
        )

        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(kwargs["match"], {"mentee_id": ObjectId(mentee_id)})

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounters_for_mentee_keeps_non_objectid_value(
        self, mock_get_mongo, mock_get_config
    ):
        """A non-ObjectId mentee id is matched as-is without raising."""
        mock_config = _make_config()
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        EncounterService.get_encounters_for_mentee(
            "not-an-object-id", self.mock_token, self.mock_breadcrumb
        )

        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(kwargs["match"], {"mentee_id": "not-an-object-id"})

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_allowed_for_mentor(self, mock_get_mongo, mock_get_config):
        """A mentor may read any encounter (no ownership check on read)."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {"_id": "123", "name": "encounter1"}
        mock_get_mongo.return_value = mock_mongo

        token = {"user_id": "mentor_user", "roles": ["mentor"]}
        result = EncounterService.get_encounter("123", token, self.mock_breadcrumb)

        self.assertEqual(result["_id"], "123")

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_allowed_for_admin(self, mock_get_mongo, mock_get_config):
        """An admin may read any encounter."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {"_id": "123", "name": "encounter1"}
        mock_get_mongo.return_value = mock_mongo

        token = {"user_id": "admin_user", "roles": ["admin"]}
        result = EncounterService.get_encounter("123", token, self.mock_breadcrumb)

        self.assertEqual(result["_id"], "123")

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_denied_for_other_role(self, mock_get_mongo, mock_get_config):
        """A caller with neither mentor nor admin role is denied (403)."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_get_mongo.return_value = mock_mongo

        token = {"user_id": "mentee_user", "roles": ["mentee"]}
        with self.assertRaises(HTTPForbidden):
            EncounterService.get_encounter("123", token, self.mock_breadcrumb)

        mock_mongo.get_document.assert_not_called()


if __name__ == "__main__":
    unittest.main()
