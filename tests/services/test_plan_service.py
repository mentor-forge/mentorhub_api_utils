"""
Unit tests for Plan service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from pymongo import ASCENDING
from api_utils.services.plan_service import PlanService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestPlanService(unittest.TestCase):
    """Test cases for PlanService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.plan_service.execute_list_query")
    @patch("api_utils.services.plan_service.Config.get_instance")
    def test_get_plans_returns_all_sorted_by_name(
        self, mock_get_config, mock_execute_list
    ):
        """get_plans returns a page (default name asc) as a plain list."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        plans = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "alpha"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "beta"},
        ]
        mock_execute_list.return_value = plans

        result = PlanService.get_plans(self.mock_token, self.mock_breadcrumb)

        self.assertEqual(result, plans)
        mock_execute_list.assert_called_once()
        call_kwargs = mock_execute_list.call_args[1]
        self.assertEqual(call_kwargs["match"], {})

    @patch("api_utils.services.plan_service.execute_list_query")
    @patch("api_utils.services.plan_service.Config.get_instance")
    def test_get_plans_applies_pagination_and_name_filter(
        self, mock_get_config, mock_execute_list
    ):
        """get_plans honors offset/size and the optional name contains filter."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config
        mock_execute_list.return_value = []

        PlanService.get_plans(
            {"user_id": "test_user", "roles": ["developer"]},
            self.mock_breadcrumb,
            offset=10,
            size=5,
            filters={"name": "intro"},
            sort_by=[("name", ASCENDING), ("_id", ASCENDING)],
        )

        call_kwargs = mock_execute_list.call_args[1]
        match = call_kwargs["match"]
        self.assertEqual(match["status"], {"$ne": "archived"})
        self.assertEqual(match["name"]["$regex"], "intro")
        self.assertEqual(call_kwargs["offset"], 10)
        self.assertEqual(call_kwargs["size"], 5)

    @patch("api_utils.services.plan_service.Config.get_instance")
    @patch("api_utils.services.plan_service.MongoIO.get_instance")
    def test_get_plan_success(self, mock_get_mongo, mock_get_config):
        """Test successful retrieval of a specific plan document."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "name": "plan1",
        }
        mock_get_mongo.return_value = mock_mongo

        result = PlanService.get_plan("123", self.mock_token, self.mock_breadcrumb)

        self.assertIsNotNone(result)
        self.assertEqual(result["_id"], "123")
        mock_mongo.get_document.assert_called_once_with("Plan", "123")

    @patch("api_utils.services.plan_service.Config.get_instance")
    @patch("api_utils.services.plan_service.MongoIO.get_instance")
    def test_get_plan_not_found(self, mock_get_mongo, mock_get_config):
        """Test get_plan raises HTTPNotFound when document not found."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound) as context:
            PlanService.get_plan("999", self.mock_token, self.mock_breadcrumb)
        self.assertIn("999", str(context.exception))

    @patch("api_utils.services.plan_service.Config.get_instance")
    @patch("api_utils.services.plan_service.MongoIO.get_instance")
    def test_get_plans_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_plans handles database exceptions."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        with patch(
            "api_utils.services.plan_service.execute_list_query",
            side_effect=Exception("Database error"),
        ):
            with self.assertRaises(HTTPInternalServerError):
                PlanService.get_plans(self.mock_token, self.mock_breadcrumb)

    @patch("api_utils.services.plan_service.Config.get_instance")
    @patch("api_utils.services.plan_service.MongoIO.get_instance")
    def test_get_plan_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_plan handles database exceptions."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            PlanService.get_plan("123", self.mock_token, self.mock_breadcrumb)

    @patch("api_utils.services.plan_service.Config.get_instance")
    @patch("api_utils.services.plan_service.MongoIO.get_instance")
    def test_get_plan_returns_checklist(self, mock_get_mongo, mock_get_config):
        """get_plan returns the stored `checklist` unchanged."""
        mock_config = MagicMock()
        mock_config.PLAN_COLLECTION_NAME = "Plan"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": "123",
            "name": "plan1",
            "checklist": ["do x", "do y"],
        }
        mock_get_mongo.return_value = mock_mongo

        result = PlanService.get_plan("123", self.mock_token, self.mock_breadcrumb)

        self.assertEqual(result["checklist"], ["do x", "do y"])


if __name__ == "__main__":
    unittest.main()
