import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from api_utils import create_config_routes

class TestConfigRoutes(unittest.TestCase):
    def setUp(self):
        """Set up the Flask test client and app context."""
        self.app = Flask(__name__)
        self.app.register_blueprint(create_config_routes(), url_prefix='/api/config')
        self.client = self.app.test_client()
    
    @patch('api_utils.routes.config_routes.create_flask_token')
    @patch('api_utils.routes.config_routes.create_flask_breadcrumb')
    def test_get_config_success(self, mock_create_breadcrumb, mock_create_token):
        """Test GET /api/config for successful response."""
        # Arrange
        mock_token = {"user_id": "mock_user"}
        mock_create_token.return_value = mock_token
        fake_breadcrumb = {"at_time":"sometime", "correlation_id":"correlation_ID"}
        mock_create_breadcrumb.return_value = fake_breadcrumb

        # Act
        response = self.client.get('/api/config')

        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json["config_items"], list)
        self.assertIsInstance(response.json["versions"], list)
        self.assertIsInstance(response.json["enumerators"], list)
        
        mock_create_token.assert_called_once()
        mock_create_breadcrumb.assert_called_once_with(mock_token)

    @patch('api_utils.routes.config_routes.create_flask_token')
    @patch('api_utils.routes.config_routes.create_flask_breadcrumb')
    def test_get_config_failure(self, mock_create_breadcrumb, mock_create_token):
        """Test GET /api/config when an exception is raised."""
        mock_create_token.side_effect = Exception("Token error")
        fake_breadcrumb = {"at_time":"sometime", "correlation_id":"correlation_ID"}
        mock_create_breadcrumb.return_value = fake_breadcrumb

        response = self.client.get('/api/config')

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "A processing error occurred"})

if __name__ == '__main__':
    unittest.main()

