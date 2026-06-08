"""
Unit tests for route wrapper exception handling.
"""
import unittest
from unittest.mock import Mock, patch
from flask import Flask, jsonify
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPUnauthorized,
    HTTPForbidden,
    HTTPInternalServerError,
)


class TestRouteWrapper(unittest.TestCase):
    """Test route wrapper exception handling."""
    
    def setUp(self):
        """Set up test Flask app."""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_handle_route_exceptions_success(self):
        """Test that successful route execution is not affected."""
        @self.app.route('/success')
        @handle_route_exceptions
        def success_route():
            return jsonify({"status": "ok"}), 200
        
        response = self.client.get('/success')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"status": "ok"})
    
    def test_handle_route_exceptions_bad_request(self):
        """Test that HTTPBadRequest is converted to 400 response."""
        @self.app.route('/bad-request')
        @handle_route_exceptions
        def bad_request_route():
            raise HTTPBadRequest("limit must be >= 1")
        
        response = self.client.get('/bad-request')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "limit must be >= 1"})
    
    def test_handle_route_exceptions_unauthorized(self):
        """Test that HTTPUnauthorized is converted to 401 response."""
        @self.app.route('/unauthorized')
        @handle_route_exceptions
        def unauthorized_route():
            raise HTTPUnauthorized("Invalid token")
        
        response = self.client.get('/unauthorized')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "Invalid token"})
    
    def test_handle_route_exceptions_forbidden(self):
        """Test that HTTPForbidden is converted to 403 response."""
        @self.app.route('/forbidden')
        @handle_route_exceptions
        def forbidden_route():
            raise HTTPForbidden("Access denied")
        
        response = self.client.get('/forbidden')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json, {"error": "Access denied"})
    
    def test_handle_route_exceptions_internal_server_error(self):
        """Test that HTTPInternalServerError is converted to 500 response."""
        @self.app.route('/error')
        @handle_route_exceptions
        def error_route():
            raise HTTPInternalServerError("Database error")
        
        response = self.client.get('/error')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Database error"})
    
    def test_handle_route_exceptions_generic_exception(self):
        """Test that generic exceptions are converted to 500 response."""
        @self.app.route('/generic-error')
        @handle_route_exceptions
        def generic_error_route():
            raise ValueError("Something went wrong")
        
        response = self.client.get('/generic-error')
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "A processing error occurred"})
    
    def test_handle_route_exceptions_preserves_function_metadata(self):
        """Test that wrapper preserves function metadata."""
        @handle_route_exceptions
        def test_function():
            """Test function docstring."""
            return "test"
        
        self.assertEqual(test_function.__name__, "test_function")
        self.assertEqual(test_function.__doc__, "Test function docstring.")


if __name__ == '__main__':
    unittest.main()

