"""
Unit tests for Aggregation service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from api_utils.services.aggregation_service import AggregationService
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
)


class TestAggregationService(unittest.TestCase):
    """Test cases for AggregationService."""

    def setUp(self):
        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }
        self.resource_id = "507f1f77bcf86cd799439011"

    @patch("api_utils.services.aggregation_service.Config.get_instance")
    @patch("api_utils.services.aggregation_service.MongoIO.get_instance")
    def test_get_aggregation_for_resource_success(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.RESOURCE_AGGREGATION_COLLECTION_NAME = "Resource_Aggregation"
        mock_config.RESOURCE_COLLECTION_NAME = "Resource"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = [
            {"_id": ObjectId(self.resource_id), "status": "active"},
            {
                "_id": ObjectId(self.resource_id),
                "note_count": 3,
            },
        ]
        mock_get_mongo.return_value = mock_mongo

        result = AggregationService.get_aggregation_for_resource(
            self.resource_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(result["note_count"], 3)

    @patch("api_utils.services.aggregation_service.Config.get_instance")
    @patch("api_utils.services.aggregation_service.MongoIO.get_instance")
    def test_get_aggregation_hidden_when_resource_archived(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.RESOURCE_AGGREGATION_COLLECTION_NAME = "Resource_Aggregation"
        mock_config.RESOURCE_COLLECTION_NAME = "Resource"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {
            "_id": ObjectId(self.resource_id),
            "status": "archived",
        }
        mock_get_mongo.return_value = mock_mongo

        token = {"user_id": "test_user", "roles": ["developer"]}
        result = AggregationService.get_aggregation_for_resource(
            self.resource_id, token, self.mock_breadcrumb
        )

        self.assertIsNone(result)

    @patch("api_utils.services.aggregation_service.Config.get_instance")
    @patch("api_utils.services.aggregation_service.MongoIO.get_instance")
    def test_get_aggregation_for_resource_not_found(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.RESOURCE_AGGREGATION_COLLECTION_NAME = "Resource_Aggregation"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_mongo.get_documents.return_value = []
        mock_get_mongo.return_value = mock_mongo

        result = AggregationService.get_aggregation_for_resource(
            self.resource_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertIsNone(result)

    @patch("api_utils.services.aggregation_service.Config.get_instance")
    @patch("api_utils.services.aggregation_service.MongoIO.get_instance")
    def test_get_aggregation_for_resource_invalid_id(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.RESOURCE_AGGREGATION_COLLECTION_NAME = "Resource_Aggregation"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPBadRequest):
            AggregationService.get_aggregation_for_resource(
                "invalid", self.mock_token, self.mock_breadcrumb
            )

    @patch("api_utils.services.aggregation_service.Config.get_instance")
    @patch("api_utils.services.aggregation_service.MongoIO.get_instance")
    def test_get_aggregation_for_resource_handles_exception(
        self, mock_get_mongo, mock_get_config
    ):
        mock_config = MagicMock()
        mock_config.RESOURCE_AGGREGATION_COLLECTION_NAME = "Resource_Aggregation"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            AggregationService.get_aggregation_for_resource(
                self.resource_id, self.mock_token, self.mock_breadcrumb
            )


if __name__ == "__main__":
    unittest.main()
