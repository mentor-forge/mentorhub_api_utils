"""
Unit tests for Journey service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

from api_utils.services.journey_service import JourneyService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


def _mock_config(mock_get_config):
    mock_config = MagicMock()
    mock_config.JOURNEY_COLLECTION_NAME = "Journey"
    mock_config.ROLE_MENTOR = "mentor"
    mock_config.ROLE_ADMIN = "admin"
    mock_get_config.return_value = mock_config
    return mock_config


class TestJourneyService(unittest.TestCase):
    """Test cases for JourneyService consume GETs."""

    def setUp(self):
        self.journey_id = "507f1f77bcf86cd799439011"
        self.mock_token = {
            "user_id": "test_user",
            "roles": ["mentee"],
            "profile_id": self.journey_id,
        }
        self.mock_admin_token = {"user_id": "admin_user", "roles": ["admin"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_success(self, mock_get_mongo, mock_get_config):
        _mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": self.journey_id,
            "profile_id": ObjectId(self.journey_id),
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey(
            self.journey_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["profile_id"], ObjectId(self.journey_id))
        mock_mongo.get_document.assert_called_once_with("Journey", self.journey_id)

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_hides_other_profile(self, mock_get_mongo, mock_get_config):
        _mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "507f1f77bcf86cd799439099",
            "profile_id": ObjectId("507f1f77bcf86cd799439099"),
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            JourneyService.get_journey(
                "507f1f77bcf86cd799439099", self.mock_token, self.mock_breadcrumb
            )

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_admin_sees_archived(self, mock_get_mongo, mock_get_config):
        _mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": self.journey_id,
            "profile_id": ObjectId("507f1f77bcf86cd799439099"),
            "status": "archived",
        }
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey(
            self.journey_id, self.mock_admin_token, self.mock_breadcrumb
        )

        self.assertEqual(result["status"], "archived")

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_not_found(self, mock_get_mongo, mock_get_config):
        _mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound) as context:
            JourneyService.get_journey(
                self.journey_id, self.mock_token, self.mock_breadcrumb
            )
        self.assertIn(self.journey_id, str(context.exception))

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_handles_exception(self, mock_get_mongo, mock_get_config):
        _mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            JourneyService.get_journey(
                self.journey_id, self.mock_token, self.mock_breadcrumb
            )


_PROGRESS_MENTEE_ID = ObjectId("507f1f77bcf86cd799439011")


class TestJourneyProgress(unittest.TestCase):
    """Active-journey resource counts by scope with outbound visibility."""

    def setUp(self):
        self.mock_token = {
            "user_id": "daniel",
            "roles": ["mentee"],
            "profile_id": str(_PROGRESS_MENTEE_ID),
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "mike",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_counts_by_scope(
        self, mock_get_mongo, mock_get_config
    ):
        """Counts library/now directly and sums resources across next topics."""
        _mock_config(mock_get_config)

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {
                "profile_id": _PROGRESS_MENTEE_ID,
                "status": "active",
                "library": [1, 2, 3],
                "now": [1],
                "next": [
                    {"resources": ["a", "b"]},
                    {"resources": ["c"]},
                ],
            }
        ]
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey_progress(
            _PROGRESS_MENTEE_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, {"library": 3, "now": 1, "next": 3})
        mock_mongo.get_documents.assert_called_once_with(
            "Journey", match={"profile_id": _PROGRESS_MENTEE_ID, "status": "active"}
        )

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_no_active_journey(
        self, mock_get_mongo, mock_get_config
    ):
        """Return zero counts when the mentee has no active journey."""
        _mock_config(mock_get_config)

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey_progress(
            _PROGRESS_MENTEE_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, {"library": 0, "now": 0, "next": 0})

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_hides_other_profile(
        self, mock_get_mongo, mock_get_config
    ):
        """Return zeros when the active journey belongs to another profile."""
        _mock_config(mock_get_config)

        other_id = ObjectId("507f1f77bcf86cd799439099")
        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {
                "profile_id": other_id,
                "status": "active",
                "library": [1, 2, 3],
                "now": [1],
                "next": [],
            }
        ]
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey_progress(
            other_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, {"library": 0, "now": 0, "next": 0})

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_handles_missing_scope_fields(
        self, mock_get_mongo, mock_get_config
    ):
        """Missing/None scope fields are treated as empty (zero counts)."""
        _mock_config(mock_get_config)

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {
                "profile_id": _PROGRESS_MENTEE_ID,
                "status": "active",
                "library": None,
                "next": None,
            }
        ]
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey_progress(
            _PROGRESS_MENTEE_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, {"library": 0, "now": 0, "next": 0})

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_encodes_string_profile_id(
        self, mock_get_mongo, mock_get_config
    ):
        """A string profile_id is encoded to ObjectId before matching."""
        _mock_config(mock_get_config)

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        JourneyService.get_journey_progress(
            str(_PROGRESS_MENTEE_ID), self.mock_token, self.mock_breadcrumb
        )

        mock_mongo.get_documents.assert_called_once_with(
            "Journey", match={"profile_id": _PROGRESS_MENTEE_ID, "status": "active"}
        )


if __name__ == "__main__":
    unittest.main()
