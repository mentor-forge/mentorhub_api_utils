"""
Unit tests for Encounter service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from pymongo import DESCENDING
from api_utils.services.encounter_service import EncounterService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)

MENTOR_ID = ObjectId("507f1f77bcf86cd799439001")
MENTEE_ID = ObjectId("507f1f77bcf86cd799439011")
OTHER_MENTOR_ID = ObjectId("507f1f77bcf86cd799439002")


def _make_config():
    """Build a config mock exposing the names/role constants the service reads."""
    mock_config = MagicMock()
    mock_config.ENCOUNTER_COLLECTION_NAME = "Encounter"
    mock_config.PROFILE_COLLECTION_NAME = "Profile"
    mock_config.ROLE_MENTOR = "mentor"
    mock_config.ROLE_ADMIN = "admin"
    return mock_config


def _mentor_token():
    return {
        "user_id": "mentor_user",
        "roles": ["mentor"],
        "profile_id": str(MENTOR_ID),
        "mentor_id": str(MENTOR_ID),
    }


def _other_mentee_token():
    return {
        "user_id": "other_mentee",
        "roles": ["mentee"],
        "profile_id": "507f1f77bcf86cd799439088",
    }


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
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "mentor_id": MENTOR_ID,
            "mentee_id": MENTEE_ID,
            "status": "active",
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
        mock_get_config.return_value = _make_config()

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
        mock_get_config.return_value = _make_config()

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
        mock_get_config.return_value = _make_config()

        encounter_id = ObjectId("507f1f77bcf86cd7994390aa")
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {
                "_id": encounter_id,
                "mentee_id": MENTEE_ID,
                "mentor_id": MENTOR_ID,
                "status": "active",
                "date": "2025-02-01T00:00:00Z",
                "tldr": "great session",
                "summary": "covered async patterns",
                "notes": "extra field not returned in summary",
            }
        ]
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_recent_encounter(
            MENTEE_ID, _mentor_token(), self.mock_breadcrumb
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
        self.assertEqual(kwargs["match"]["mentee_id"], MENTEE_ID)
        self.assertEqual(kwargs["sort_by"], [("date", DESCENDING)])

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_recent_encounter_none_when_no_encounters(
        self, mock_get_mongo, mock_get_config
    ):
        """Return None when the mentee has no visible encounters."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_recent_encounter(
            MENTEE_ID,
            _mentor_token(),
            self.mock_breadcrumb,
        )

        self.assertIsNone(result)

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounters_for_mentee_returns_sorted_list(
        self, mock_get_mongo, mock_get_config
    ):
        """All of a mentee's visible encounters are returned, most recent first."""
        mock_get_config.return_value = _make_config()

        newer = {
            "_id": ObjectId("507f1f77bcf86cd7994390aa"),
            "mentor_id": MENTOR_ID,
            "mentee_id": MENTEE_ID,
            "status": "active",
            "date": "2025-03-01",
        }
        older = {
            "_id": ObjectId("507f1f77bcf86cd7994390a1"),
            "mentor_id": MENTOR_ID,
            "mentee_id": MENTEE_ID,
            "status": "active",
            "date": "2025-01-01",
        }
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [newer, older]
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_encounters_for_mentee(
            MENTEE_ID, _mentor_token(), self.mock_breadcrumb
        )

        self.assertEqual(result, [newer, older])
        mock_mongo.get_documents.assert_called_once()
        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(args[0], "Encounter")
        self.assertEqual(kwargs["match"]["mentee_id"], MENTEE_ID)
        self.assertEqual(kwargs["sort_by"], [("date", DESCENDING)])

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounters_for_mentee_converts_string_id(
        self, mock_get_mongo, mock_get_config
    ):
        """A string mentee id is normalized to ObjectId for the direct query."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        mentee_id = "507f1f77bcf86cd799439011"
        EncounterService.get_encounters_for_mentee(
            mentee_id, _mentor_token(), self.mock_breadcrumb
        )

        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(kwargs["match"]["mentee_id"], ObjectId(mentee_id))

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounters_for_mentee_keeps_non_objectid_value(
        self, mock_get_mongo, mock_get_config
    ):
        """A non-ObjectId mentee id is matched as-is without raising."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        EncounterService.get_encounters_for_mentee(
            "not-an-object-id", _mentor_token(), self.mock_breadcrumb
        )

        args, kwargs = mock_mongo.get_documents.call_args
        self.assertEqual(kwargs["match"]["mentee_id"], "not-an-object-id")

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_allowed_for_mentor(self, mock_get_mongo, mock_get_config):
        """A mentor may read encounters they mentor."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "mentor_id": MENTOR_ID,
            "mentee_id": MENTEE_ID,
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = EncounterService.get_encounter(
            "123", _mentor_token(), self.mock_breadcrumb
        )

        self.assertEqual(result["_id"], "123")

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_allowed_for_admin(self, mock_get_mongo, mock_get_config):
        """An admin may read any encounter."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "mentor_id": OTHER_MENTOR_ID,
            "status": "archived",
        }
        mock_get_mongo.return_value = mock_mongo

        token = {"user_id": "admin_user", "roles": ["admin"]}
        result = EncounterService.get_encounter("123", token, self.mock_breadcrumb)

        self.assertEqual(result["_id"], "123")

    @patch("api_utils.services.encounter_service.Config.get_instance")
    @patch("api_utils.services.encounter_service.MongoIO.get_instance")
    def test_get_encounter_hidden_for_unrelated_caller(
        self, mock_get_mongo, mock_get_config
    ):
        """A caller outside outbound scope gets 404, not 403."""
        mock_get_config.return_value = _make_config()

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "mentor_id": OTHER_MENTOR_ID,
            "mentee_id": MENTEE_ID,
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            EncounterService.get_encounter(
                "123", _other_mentee_token(), self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
