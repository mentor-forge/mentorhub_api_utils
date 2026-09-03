"""
Unit tests for Notification service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from pymongo import DESCENDING
from api_utils.services.notification_service import NotificationService
from api_utils.flask_utils.exceptions import HTTPInternalServerError
from api_utils.mongo_utils.list_query import DEFAULT_OFFSET, DEFAULT_SIZE

CREATED_ID = "507f1f77bcf86cd799439011"
PROFILE_ID = "507f1f77bcf86cd799439021"
CUSTOMER_ID = "507f1f77bcf86cd799439022"


class TestNotificationService(unittest.TestCase):
    """Test cases for NotificationService."""

    def setUp(self):
        self.mock_token = {
            "user_id": "test_user",
            "display_name": "Test User",
            "roles": ["admin"],
            "profile_id": PROFILE_ID,
            "customer_id": CUSTOMER_ID,
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
            "name": "Invite pending",
            "message": "You have a new invite to review.",
            "profile_id": PROFILE_ID,
            "status": "active",
        }

    @patch("api_utils.services.notification_service.Config.get_instance")
    @patch("api_utils.services.notification_service.MongoIO.get_instance")
    def test_create_notification_success(self, mock_get_mongo, mock_get_config):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        notification = NotificationService.create_notification(
            dict(self.sample_data), self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(str(notification["_id"]), CREATED_ID)
        mock_mongo.create_document.assert_called_once()
        collection_name, created_data = mock_mongo.create_document.call_args[0]
        self.assertEqual(collection_name, "Notification")
        self.assertEqual(created_data["name"], "Invite pending")
        self.assertEqual(created_data["message"], "You have a new invite to review.")
        self.assertEqual(created_data["profile_id"], ObjectId(PROFILE_ID))
        self.assertEqual(created_data["created"], self.mock_breadcrumb)
        self.assertNotIn("saved", created_data)
        self.assertNotIn("dismissed", created_data)

    @patch("api_utils.services.notification_service.Config.get_instance")
    @patch("api_utils.services.notification_service.MongoIO.get_instance")
    def test_create_notification_strips_client_ids(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        data = {"_id": "should-be-removed", **self.sample_data}

        result = NotificationService.create_notification(
            data, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(str(result["_id"]), CREATED_ID)
        self.assertNotEqual(str(result["_id"]), "should-be-removed")
        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertEqual(created_data["_id"], ObjectId(CREATED_ID))

    @patch("api_utils.services.notification_service.Config.get_instance")
    @patch("api_utils.services.notification_service.MongoIO.get_instance")
    def test_create_notification_does_not_set_saved(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.return_value = CREATED_ID
        mock_get_mongo.return_value = mock_mongo

        data = {**self.sample_data, "saved": self.mock_breadcrumb}

        NotificationService.create_notification(
            data, self.mock_token, self.mock_breadcrumb
        )

        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertNotIn("saved", created_data)
        self.assertEqual(created_data["created"], self.mock_breadcrumb)

    @patch("api_utils.services.notification_service.Config.get_instance")
    @patch("api_utils.services.notification_service.MongoIO.get_instance")
    def test_create_notification_strips_client_created(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
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

        NotificationService.create_notification(
            data, self.mock_token, self.mock_breadcrumb
        )

        created_data = mock_mongo.create_document.call_args[0][1]
        self.assertEqual(created_data["created"], self.mock_breadcrumb)
        self.assertNotEqual(created_data["created"], client_created)

    @patch("api_utils.services.notification_service.Config.get_instance")
    @patch("api_utils.services.notification_service.MongoIO.get_instance")
    def test_create_notification_handles_exception(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.create_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            NotificationService.create_notification(
                dict(self.sample_data), self.mock_token, self.mock_breadcrumb
            )

    @patch("api_utils.services.notification_service.execute_list_query")
    @patch("api_utils.services.notification_service.Config.get_instance")
    def test_get_notifications_success(self, mock_get_config, mock_execute_list):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config
        mock_execute_list.return_value = [{"_id": "1", "name": "Invite pending"}]

        notifications = NotificationService.get_notifications(
            self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(len(notifications), 1)
        mock_execute_list.assert_called_once()
        args, kwargs = mock_execute_list.call_args
        self.assertEqual(args[0], "Notification")
        self.assertEqual(kwargs["offset"], DEFAULT_OFFSET)
        self.assertEqual(kwargs["size"], DEFAULT_SIZE)
        self.assertEqual(kwargs["match"], {})
        self.assertEqual(
            kwargs["sort_by"],
            [("created.at_time", DESCENDING), ("_id", DESCENDING)],
        )

    @patch("api_utils.services.notification_service.execute_list_query")
    @patch("api_utils.services.notification_service.Config.get_instance")
    def test_get_notifications_outbound_includes_global_and_own_ids(
        self, mock_get_config, mock_execute_list
    ):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config
        mock_execute_list.return_value = []

        token = {
            "user_id": "carol",
            "roles": ["customer"],
            "profile_id": PROFILE_ID,
            "customer_id": CUSTOMER_ID,
        }
        NotificationService.get_notifications(token, self.mock_breadcrumb)

        match = mock_execute_list.call_args.kwargs["match"]
        self.assertEqual(match["status"], {"$ne": "archived"})
        or_clauses = match["$or"]
        self.assertIn({"global": {"$exists": True}}, or_clauses)
        profile_ids = [clause.get("profile_id") for clause in or_clauses]
        customer_ids = [clause.get("customer_id") for clause in or_clauses]
        self.assertIn(ObjectId(PROFILE_ID), profile_ids)
        self.assertIn(ObjectId(CUSTOMER_ID), customer_ids)

    @patch("api_utils.services.notification_service.execute_list_query")
    @patch("api_utils.services.notification_service.Config.get_instance")
    def test_get_notifications_encodes_match_ids(
        self, mock_get_config, mock_execute_list
    ):
        mock_config = MagicMock()
        mock_config.NOTIFICATION_COLLECTION_NAME = "Notification"
        mock_get_config.return_value = mock_config
        mock_execute_list.return_value = []

        NotificationService.get_notifications(
            self.mock_token,
            self.mock_breadcrumb,
            match={"profile_id": PROFILE_ID},
        )

        call_kwargs = mock_execute_list.call_args[1]
        self.assertEqual(call_kwargs["match"]["profile_id"], ObjectId(PROFILE_ID))

    def test_shared_service_has_no_dismiss_notification(self):
        self.assertFalse(hasattr(NotificationService, "dismiss_notification"))


if __name__ == "__main__":
    unittest.main()
