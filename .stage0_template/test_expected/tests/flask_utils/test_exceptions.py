"""
Unit tests for custom HTTP exceptions.
"""
import unittest
from api_utils.flask_utils.exceptions import HTTPUnauthorized, HTTPForbidden, HTTPInternalServerError


class TestExceptions(unittest.TestCase):
    """Test custom HTTP exception classes."""
    
    def test_http_unauthorized_default_message(self):
        """Test HTTPUnauthorized with default message."""
        exc = HTTPUnauthorized()
        self.assertEqual(exc.status_code, 401)
        self.assertEqual(exc.message, "Unauthorized")
        self.assertEqual(str(exc), "Unauthorized")
    
    def test_http_unauthorized_custom_message(self):
        """Test HTTPUnauthorized with custom message."""
        exc = HTTPUnauthorized("Invalid token")
        self.assertEqual(exc.status_code, 401)
        self.assertEqual(exc.message, "Invalid token")
        self.assertEqual(str(exc), "Invalid token")
    
    def test_http_forbidden_default_message(self):
        """Test HTTPForbidden with default message."""
        exc = HTTPForbidden()
        self.assertEqual(exc.status_code, 403)
        self.assertEqual(exc.message, "Forbidden")
        self.assertEqual(str(exc), "Forbidden")
    
    def test_http_forbidden_custom_message(self):
        """Test HTTPForbidden with custom message."""
        exc = HTTPForbidden("Access denied")
        self.assertEqual(exc.status_code, 403)
        self.assertEqual(exc.message, "Access denied")
        self.assertEqual(str(exc), "Access denied")
    
    def test_http_internal_server_error_default_message(self):
        """Test HTTPInternalServerError with default message."""
        exc = HTTPInternalServerError()
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.message, "Internal Server Error")
        self.assertEqual(str(exc), "Internal Server Error")
    
    def test_http_internal_server_error_custom_message(self):
        """Test HTTPInternalServerError with custom message."""
        exc = HTTPInternalServerError("Database connection failed")
        self.assertEqual(exc.status_code, 500)
        self.assertEqual(exc.message, "Database connection failed")
        self.assertEqual(str(exc), "Database connection failed")


if __name__ == '__main__':
    unittest.main()

