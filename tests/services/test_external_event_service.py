"""
Unit tests for ExternalEvent service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from api_utils.services.external_event_service import ExternalEventService
from api_utils.flask_utils.exceptions import HTTPInternalServerError

CREATED_ID = "507f1f77bcf86cd799439011"


class TestExternalEventService(unittest.TestCase):
    """Test cases for ExternalEventService."""

    def setUp(self):
        self.mock_token = {
            "user_id": "test_user",
            "display_name": "Test User",
            "roles": ["admin"],
            "profile_id": "507f1f77bcf86cd799439011",
            "customer_id": "507f1f77bcf86cd799439012",
            "mentor_id": "",
            "remote_ip": "127.0.0.1",
        }
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }
        self.sample_data = {
            "source": "stripe",
            "external_id": "evt_123",
            "payload_hash": "abc123hash",
            "normalized_body": {"type": "invoice.paid"},
        }

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_create_external_event_success(self, mock_get_mongo, mock_get_config):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        event = ExternalEventService.create_external_event(
            dict(self.sample_data), self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(str(event["_id"]), CREATED_ID)
        mock_mongo.create_document.assert_called_once()
        collection_name, created_data = mock_mongo.create_document.call_args[0]
        self.assertEqual(collection_name, "ExternalEvent")
        self.assertEqual(created_data["source"], "stripe")
        self.assertEqual(created_data["external_id"], "evt_123")
        self.assertEqual(created_data["payload_hash"], "abc123hash")
        self.assertEqual(created_data["normalized_body"], {"type": "invoice.paid"})
        self.assertEqual(created_data["created"], self.mock_breadcrumb)
        self.assertNotIn("saved", created_data)

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_create_external_event_removes_id(self, mock_get_mongo, mock_get_config):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        data = {"_id": "should-be-removed", **self.sample_data}

        result = ExternalEventService.create_external_event(
            data, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(str(result["_id"]), CREATED_ID)
        self.assertNotEqual(str(result["_id"]), "should-be-removed")
        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertEqual(created_data["_id"], ObjectId(CREATED_ID))

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_create_external_event_strips_client_created(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        client_created = {
            "at_time": "1999-01-01T00:00:00Z",
            "by_user": "attacker",
            "from_ip": "0.0.0.0",
            "correlation_id": "forged",
        }
        data = {**self.sample_data, "created": client_created}

        ExternalEventService.create_external_event(
            data, self.mock_token, self.mock_breadcrumb
        )

        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertEqual(created_data["created"], self.mock_breadcrumb)
        self.assertNotEqual(created_data["created"], client_created)

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_create_external_event_does_not_set_saved(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        ExternalEventService.create_external_event(
            dict(self.sample_data), self.mock_token, self.mock_breadcrumb
        )

        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertNotIn("saved", created_data)

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_create_external_event_leaves_external_id_as_string(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        ExternalEventService.create_external_event(
            dict(self.sample_data), self.mock_token, self.mock_breadcrumb
        )

        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertIsInstance(created_data["external_id"], str)
        self.assertEqual(created_data["external_id"], "evt_123")

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_create_external_event_handles_exception(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            ExternalEventService.create_external_event(
                dict(self.sample_data), self.mock_token, self.mock_breadcrumb
            )

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_get_external_event_success(self, mock_get_mongo, mock_get_config):
        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId(CREATED_ID),
            **self.sample_data,
        }
        mock_get_mongo.return_value = mock_mongo

        result = ExternalEventService.get_external_event(
            CREATED_ID, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(str(result["_id"]), CREATED_ID)
        mock_mongo.get_document.assert_called_once_with("ExternalEvent", CREATED_ID)

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_get_external_event_hidden_for_non_admin(
        self, mock_get_mongo, mock_get_config
    ):
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId(CREATED_ID),
            **self.sample_data,
        }
        mock_get_mongo.return_value = mock_mongo

        token = {"user_id": "test_user", "roles": ["developer"]}
        with self.assertRaises(HTTPNotFound):
            ExternalEventService.get_external_event(
                CREATED_ID, token, self.mock_breadcrumb
            )

    @patch("api_utils.services.external_event_service.Config.get_instance")
    @patch("api_utils.services.external_event_service.MongoIO.get_instance")
    def test_get_external_event_not_found(self, mock_get_mongo, mock_get_config):
        from api_utils.flask_utils.exceptions import HTTPNotFound

        mock_config = MagicMock()
        mock_config.EXTERNAL_EVENT_COLLECTION_NAME = "ExternalEvent"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound):
            ExternalEventService.get_external_event(
                "999", self.mock_token, self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
