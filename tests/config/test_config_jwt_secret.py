"""
Unit tests for JWT_SECRET validation in Config.
"""
import unittest
import os
from api_utils import Config


class TestJWTSecretValidation(unittest.TestCase):
    """Test JWT_SECRET validation and security enforcement."""
    
    def setUp(self):
        """Clear config instance before each test."""
        Config._instance = None
        # Clear JWT_SECRET from environment if it exists
        if 'JWT_SECRET' in os.environ:
            self._saved_jwt_secret = os.environ['JWT_SECRET']
            del os.environ['JWT_SECRET']
        else:
            self._saved_jwt_secret = None
    
    def tearDown(self):
        """Restore JWT_SECRET after test."""
        Config._instance = None
        if self._saved_jwt_secret is not None:
            os.environ['JWT_SECRET'] = self._saved_jwt_secret
        elif 'JWT_SECRET' in os.environ:
            del os.environ['JWT_SECRET']
    
    def test_jwt_secret_default_value_raises_error(self):
        """Test that using default JWT_SECRET raises ValueError on initialization."""
        # Ensure JWT_SECRET is not in environment (will use default)
        if 'JWT_SECRET' in os.environ:
            del os.environ['JWT_SECRET']
        
        # Should raise ValueError when trying to initialize with default JWT_SECRET
        with self.assertRaises(ValueError) as context:
            Config.get_instance()
        
        self.assertIn("JWT_SECRET must be explicitly set", str(context.exception))
        self.assertIn("security reasons", str(context.exception))
    
    def test_jwt_secret_custom_value_succeeds(self):
        """Test that custom JWT_SECRET value allows initialization."""
        # Set custom JWT_SECRET
        os.environ['JWT_SECRET'] = 'my-custom-secret-value'
        
        # Should succeed with custom value
        config = Config.get_instance()
        
        self.assertEqual(config.JWT_SECRET, 'my-custom-secret-value')
        
        # Clean up
        del os.environ['JWT_SECRET']
    
    def test_jwt_secret_from_file_succeeds(self):
        """Test that JWT_SECRET from file allows initialization."""
        import tempfile
        from pathlib import Path
        
        # Create temporary config folder with JWT_SECRET file
        with tempfile.TemporaryDirectory() as tmpdir:
            config_folder = Path(tmpdir)
            jwt_secret_file = config_folder / "JWT_SECRET"
            jwt_secret_file.write_text("file-based-secret")
            
            # Set CONFIG_FOLDER to temp directory
            os.environ['CONFIG_FOLDER'] = str(config_folder)
            
            # Should succeed with file-based secret
            config = Config.get_instance()
            
            self.assertEqual(config.JWT_SECRET, 'file-based-secret')
            
            # Clean up
            del os.environ['CONFIG_FOLDER']


if __name__ == '__main__':
    unittest.main()
