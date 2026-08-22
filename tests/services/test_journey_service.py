"""
Unit tests for Journey service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId

from api_utils.services.journey_service import JourneyService
from api_utils.flask_utils.exceptions import (
    HTTPForbidden,
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestJourneyService(unittest.TestCase):
    """Test cases for JourneyService consume GETs."""

    def setUp(self):
        self.journey_id = "A00000000000000000000099"
        self.mock_token = {
            "user_id": "test_user",
            "roles": ["admin"],
            "profile_id": self.journey_id,
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    def _mock_config(self, mock_get_config):
        mock_config = MagicMock()
        mock_config.JOURNEY_COLLECTION_NAME = "Journey"
        mock_get_config.return_value = mock_config
        return mock_config

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_success(self, mock_get_mongo, mock_get_config):
        self._mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": self.journey_id,
            "profile_id": self.journey_id,
            "status": "active",
        }
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey(
            self.journey_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["_id"], self.journey_id)
        mock_mongo.get_document.assert_called_once_with("Journey", self.journey_id)

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_not_found(self, mock_get_mongo, mock_get_config):
        self._mock_config(mock_get_config)
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
        self._mock_config(mock_get_config)
        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            JourneyService.get_journey(
                self.journey_id, self.mock_token, self.mock_breadcrumb
            )


_PROGRESS_MENTEE_ID = ObjectId("507f1f77bcf86cd799439011")


def _progress_config():
    """Minimal Config mock for the mentor-dashboard progress aggregation."""
    mock_config = MagicMock()
    mock_config.JOURNEY_COLLECTION_NAME = "Journey"
    mock_config.ROLE_MENTOR = "mentor"
    mock_config.ROLE_ADMIN = "admin"
    return mock_config


class TestJourneyProgress(unittest.TestCase):
    """Harvested from Mentor API: active-journey resource counts by scope."""

    def setUp(self):
        self.mock_token = {"user_id": "mike", "roles": ["mentor"]}
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
        mock_get_config.return_value = _progress_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {
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
        mock_get_config.return_value = _progress_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey_progress(
            _PROGRESS_MENTEE_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, {"library": 0, "now": 0, "next": 0})

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_handles_missing_scope_fields(
        self, mock_get_mongo, mock_get_config
    ):
        """Missing/None scope fields are treated as empty (zero counts)."""
        mock_get_config.return_value = _progress_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = [
            {"status": "active", "library": None, "next": None}
        ]
        mock_get_mongo.return_value = mock_mongo

        result = JourneyService.get_journey_progress(
            _PROGRESS_MENTEE_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result, {"library": 0, "now": 0, "next": 0})

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_forbidden_without_mentor_role(
        self, mock_get_mongo, mock_get_config
    ):
        """Callers lacking the mentor role are denied before any DB access."""
        mock_get_config.return_value = _progress_config()
        mock_mongo = MagicMock()
        mock_get_mongo.return_value = mock_mongo

        non_mentor_token = {"user_id": "carol", "roles": ["coordinator"]}
        with self.assertRaises(HTTPForbidden):
            JourneyService.get_journey_progress(
                _PROGRESS_MENTEE_ID, non_mentor_token, self.mock_breadcrumb
            )

        mock_mongo.get_documents.assert_not_called()

    @patch("api_utils.services.journey_service.Config.get_instance")
    @patch("api_utils.services.journey_service.MongoIO.get_instance")
    def test_get_journey_progress_encodes_string_profile_id(
        self, mock_get_mongo, mock_get_config
    ):
        """A string profile_id is encoded to ObjectId before matching.

        Journey.profile_id is stored as a BSON ObjectId, and
        MongoIO.get_documents does not coerce match values, so the service must
        encode the id itself; otherwise a string profile_id silently matches
        nothing.
        """
        mock_get_config.return_value = _progress_config()

        mock_mongo = MagicMock()
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        JourneyService.get_journey_progress(
            str(_PROGRESS_MENTEE_ID), self.mock_token, self.mock_breadcrumb
        )

        # The string id must have been encoded to the equivalent ObjectId.
        mock_mongo.get_documents.assert_called_once_with(
            "Journey", match={"profile_id": _PROGRESS_MENTEE_ID, "status": "active"}
        )


if __name__ == "__main__":
    unittest.main()
