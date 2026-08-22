"""
Unit tests for Path service (consume-style, read-only).
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from api_utils.services.path_service import PathService
from api_utils.flask_utils.exceptions import (
    HTTPNotFound,
    HTTPInternalServerError,
)


class TestPathService(unittest.TestCase):
    """Test cases for PathService."""

    def setUp(self):
        """Set up the test fixture."""
        self.mock_token = {"user_id": "test_user", "roles": ["developer"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }

    @patch("api_utils.services.path_service.execute_list_query")
    @patch("api_utils.services.path_service.Config.get_instance")
    def test_get_paths_returns_sorted_list(self, mock_get_config, mock_execute_list):
        """Test successful retrieval of paths as a paginated list."""
        mock_config = MagicMock()
        mock_config.PATH_COLLECTION_NAME = "Path"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_execute_list.return_value = [
            {"_id": ObjectId("507f1f77bcf86cd799439011"), "name": "alpha"},
            {"_id": ObjectId("507f1f77bcf86cd799439012"), "name": "beta"},
        ]

        result = PathService.get_paths(self.mock_token, self.mock_breadcrumb)

        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        mock_execute_list.assert_called_once()
        call_kwargs = mock_execute_list.call_args[1]
        self.assertEqual(call_kwargs["offset"], 0)
        self.assertEqual(call_kwargs["size"], 20)

    @patch("api_utils.services.path_service.Config.get_instance")
    @patch("api_utils.services.path_service.MongoIO.get_instance")
    def test_get_path_returns_raw_document(self, mock_get_mongo, mock_get_config):
        """Test get_path returns the raw path document with resource ids."""
        mock_config = MagicMock()
        mock_config.PATH_COLLECTION_NAME = "Path"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        resource_id = "507f1f77bcf86cd799439011"
        path_doc = {
            "_id": "123",
            "name": "path1",
            "modules": [
                {
                    "name": "module1",
                    "topics": [
                        {
                            "name": "topic1",
                            "resources": [resource_id],
                        }
                    ],
                }
            ],
        }
        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = path_doc
        mock_get_mongo.return_value = mock_mongo

        result = PathService.get_path("123", self.mock_token, self.mock_breadcrumb)

        self.assertEqual(result["_id"], "123")
        resources = result["modules"][0]["topics"][0]["resources"]
        self.assertEqual(resources, [resource_id])

    @patch("api_utils.services.path_service.Config.get_instance")
    @patch("api_utils.services.path_service.MongoIO.get_instance")
    def test_get_path_without_modules(self, mock_get_mongo, mock_get_config):
        """Test get_path handles paths with no modules."""
        mock_config = MagicMock()
        mock_config.PATH_COLLECTION_NAME = "Path"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = {"_id": "123", "name": "path1"}
        mock_get_mongo.return_value = mock_mongo

        result = PathService.get_path("123", self.mock_token, self.mock_breadcrumb)

        self.assertEqual(result["_id"], "123")

    @patch("api_utils.services.path_service.Config.get_instance")
    @patch("api_utils.services.path_service.MongoIO.get_instance")
    def test_get_path_not_found(self, mock_get_mongo, mock_get_config):
        """Test get_path raises HTTPNotFound when document not found."""
        mock_config = MagicMock()
        mock_config.PATH_COLLECTION_NAME = "Path"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.return_value = None
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPNotFound) as context:
            PathService.get_path("999", self.mock_token, self.mock_breadcrumb)
        self.assertIn("999", str(context.exception))

    @patch("api_utils.services.path_service.execute_list_query")
    @patch("api_utils.services.path_service.Config.get_instance")
    def test_get_paths_handles_exception(self, mock_get_config, mock_execute_list):
        """Test get_paths handles exceptions properly."""
        mock_config = MagicMock()
        mock_config.PATH_COLLECTION_NAME = "Path"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config
        mock_execute_list.side_effect = Exception("Database error")

        with self.assertRaises(HTTPInternalServerError):
            PathService.get_paths(self.mock_token, self.mock_breadcrumb)

    @patch("api_utils.services.path_service.Config.get_instance")
    @patch("api_utils.services.path_service.MongoIO.get_instance")
    def test_get_path_handles_exception(self, mock_get_mongo, mock_get_config):
        """Test get_path handles exceptions properly."""
        mock_config = MagicMock()
        mock_config.PATH_COLLECTION_NAME = "Path"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        mock_mongo = MagicMock()
        mock_mongo.get_document.side_effect = Exception("Database error")
        mock_get_mongo.return_value = mock_mongo

        with self.assertRaises(HTTPInternalServerError):
            PathService.get_path("123", self.mock_token, self.mock_breadcrumb)

    def test_check_permission_requires_token_only(self):
        """Shared reads require a valid token; outbound filtering is separate."""
        PathService._check_permission(self.mock_token, "read")


if __name__ == "__main__":
    unittest.main()
