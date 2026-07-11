"""
Unit tests for Token class and create_flask_token function.
"""
import os
import unittest
from unittest.mock import Mock, patch
from datetime import datetime, timezone, timedelta
import jwt
from api_utils.flask_utils.token import Token, create_flask_token
from api_utils.flask_utils.exceptions import HTTPUnauthorized
from api_utils import Config


class TestToken(unittest.TestCase):
    """Test Token class JWT extraction and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        Config._instance = None
        # Set JWT_SECRET before initializing config to avoid validation error
        os.environ['JWT_SECRET'] = 'test-secret-for-token-tests'
        self.config = Config.get_instance()
    
    def _create_test_jwt(
        self,
        subject="test-user-123",
        roles=["developer"],
        expires_in_minutes=60,
        profile_id="A00000000000000000000001",
        customer_id="D00000000000000000000006",
        mentor_id="",
        name="Test User",
        include_profile_id=True,
    ):
        """Helper to create a test JWT token."""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=expires_in_minutes)
        secret = self.config.JWT_SECRET
        algorithm = self.config.JWT_ALGORITHM
        
        claims = {
            "iss": self.config.JWT_ISSUER,
            "aud": self.config.JWT_AUDIENCE,
            "sub": subject,
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "roles": roles,
            "name": name,
            "customer_id": customer_id,
            "mentor_id": mentor_id,
        }
        if include_profile_id:
            claims["profile_id"] = profile_id
        
        return jwt.encode(claims, secret, algorithm=algorithm)
    
    def test_token_extraction_success(self):
        """Test successful token extraction from Authorization header."""
        token_string = self._create_test_jwt()
        
        # Create mock request with Authorization header
        mock_request = Mock()
        mock_request.headers = {"Authorization": f"Bearer {token_string}"}
        mock_request.remote_addr = "127.0.0.1"
        
        token = Token(request_obj=mock_request)
        
        self.assertEqual(token.claims.get('sub'), "test-user-123")
        self.assertEqual(token.claims.get('user_id'), "test-user-123")
        self.assertEqual(token.claims.get('name'), "Test User")
        self.assertEqual(token.claims.get('roles'), ["developer"])
        self.assertEqual(token.claims.get('profile_id'), "A00000000000000000000001")
        self.assertEqual(token.claims.get('customer_id'), "D00000000000000000000006")
        self.assertEqual(token.claims.get('mentor_id'), "")
        self.assertEqual(token.remote_ip, "127.0.0.1")
    
    def test_token_missing_authorization_header(self):
        """Test that missing Authorization header raises HTTPUnauthorized."""
        mock_request = Mock()
        mock_request.headers = {}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("Authorization header", str(context.exception.message))
    
    def test_token_invalid_authorization_format(self):
        """Test that invalid Authorization format raises HTTPUnauthorized."""
        mock_request = Mock()
        mock_request.headers = {"Authorization": "InvalidFormat token"}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("Authorization header", str(context.exception.message))
    
    def test_token_empty_bearer_token(self):
        """Test that empty Bearer token raises HTTPUnauthorized."""
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer "}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("Empty token", str(context.exception.message))
    
    def test_token_expired(self):
        """Test that expired token raises HTTPUnauthorized."""
        # Create an expired token (expires 1 minute ago)
        token_string = self._create_test_jwt(expires_in_minutes=-1)
        
        mock_request = Mock()
        mock_request.headers = {"Authorization": f"Bearer {token_string}"}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("expired", str(context.exception.message))
    
    def test_token_invalid_jwt(self):
        """Test that invalid JWT raises HTTPUnauthorized."""
        mock_request = Mock()
        mock_request.headers = {"Authorization": "Bearer invalid.jwt.token"}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("Invalid token", str(context.exception.message))
    
    def test_token_missing_profile_id(self):
        """Test that missing profile_id claim raises HTTPUnauthorized."""
        token_string = self._create_test_jwt(include_profile_id=False)
        
        mock_request = Mock()
        mock_request.headers = {"Authorization": f"Bearer {token_string}"}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("profile_id", str(context.exception.message))
    
    def test_token_empty_profile_id(self):
        """Test that empty profile_id claim raises HTTPUnauthorized."""
        token_string = self._create_test_jwt(profile_id="")
        
        mock_request = Mock()
        mock_request.headers = {"Authorization": f"Bearer {token_string}"}
        mock_request.remote_addr = "127.0.0.1"
        
        with self.assertRaises(HTTPUnauthorized) as context:
            Token(request_obj=mock_request)
        
        self.assertIn("profile_id", str(context.exception.message))
    
    def test_token_defaults_missing_customer_and_mentor_ids(self):
        """Test that missing customer_id and mentor_id default to empty strings."""
        now = datetime.now(timezone.utc)
        exp = now + timedelta(minutes=60)
        claims = {
            "iss": self.config.JWT_ISSUER,
            "aud": self.config.JWT_AUDIENCE,
            "sub": "test-user-123",
            "iat": int(now.timestamp()),
            "exp": int(exp.timestamp()),
            "roles": ["developer"],
            "profile_id": "A00000000000000000000001",
        }
        token_string = jwt.encode(
            claims,
            self.config.JWT_SECRET,
            algorithm=self.config.JWT_ALGORITHM,
        )
        
        mock_request = Mock()
        mock_request.headers = {"Authorization": f"Bearer {token_string}"}
        mock_request.remote_addr = "127.0.0.1"
        
        token = Token(request_obj=mock_request)
        
        self.assertEqual(token.claims.get('customer_id'), "")
        self.assertEqual(token.claims.get('mentor_id'), "")
    
    def test_token_to_dict(self):
        """Test token to_dict method."""
        token_string = self._create_test_jwt(
            subject="user-456",
            roles=["admin", "user"],
            profile_id="A00000000000000000000002",
            customer_id="D00000000000000000000002",
            mentor_id="A00000000000000000000006",
            name="User 456",
        )
        
        mock_request = Mock()
        mock_request.headers = {"Authorization": f"Bearer {token_string}"}
        mock_request.remote_addr = "192.168.1.1"
        
        token = Token(request_obj=mock_request)
        token_dict = token.to_dict()
        
        self.assertEqual(token_dict["user_id"], "user-456")
        self.assertEqual(token_dict["name"], "User 456")
        self.assertEqual(token_dict["roles"], ["admin", "user"])
        self.assertEqual(token_dict["profile_id"], "A00000000000000000000002")
        self.assertEqual(token_dict["customer_id"], "D00000000000000000000002")
        self.assertEqual(token_dict["mentor_id"], "A00000000000000000000006")
        self.assertEqual(token_dict["remote_ip"], "192.168.1.1")
    
    def test_create_flask_token_success(self):
        """Test create_flask_token function with valid JWT."""
        from flask import Flask
        app = Flask(__name__)
        token_string = self._create_test_jwt(
            subject="flask-user",
            roles=["developer"],
            profile_id="A00000000000000000000001",
            name="Flask User",
        )
        
        with app.test_request_context(
            '/test',
            headers={"Authorization": f"Bearer {token_string}"},
            environ_base={'REMOTE_ADDR': '10.0.0.1'}
        ):
            token_dict = create_flask_token()
            
            self.assertEqual(token_dict["user_id"], "flask-user")
            self.assertEqual(token_dict["name"], "Flask User")
            self.assertEqual(token_dict["roles"], ["developer"])
            self.assertEqual(token_dict["profile_id"], "A00000000000000000000001")
            self.assertEqual(token_dict["customer_id"], "D00000000000000000000006")
            self.assertEqual(token_dict["mentor_id"], "")
            self.assertEqual(token_dict["remote_ip"], "10.0.0.1")
    
    def test_create_flask_token_missing_header(self):
        """Test create_flask_token raises HTTPUnauthorized when header missing."""
        from flask import Flask
        app = Flask(__name__)
        
        with app.test_request_context(
            '/test',
            environ_base={'REMOTE_ADDR': '10.0.0.1'}
        ):
            with self.assertRaises(HTTPUnauthorized):
                create_flask_token()


if __name__ == '__main__':
    unittest.main()
