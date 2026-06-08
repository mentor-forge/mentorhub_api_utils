import json
import unittest
import os
from api_utils import Config

class TestConfigDefaults(unittest.TestCase):

    def setUp(self):
        """Re-initialize the config for each test."""
        # Clear environment variables to ensure defaults are tested
        # Get config instance first to access config keys
        Config._instance = None
        
        # Set JWT_SECRET to avoid validation error (we're testing defaults, not JWT_SECRET validation)
        os.environ['JWT_SECRET'] = 'test-secret-for-defaults-testing'
        
        temp_config = Config.get_instance()
        
        # Store and clear all config-related environment variables
        self._saved_env = {}
        all_keys = {
            **temp_config.config_strings,
            **temp_config.config_ints,
            **temp_config.config_booleans,
            **temp_config.config_string_secrets,
            **temp_config.config_json_secrets,
            **temp_config.config_json_defaults
        }
        
        for key in all_keys:
            if key != "BUILT_AT" and key != "CONFIG_FOLDER" and key != "JWT_SECRET":
                if key in os.environ:
                    self._saved_env[key] = os.environ[key]
                    del os.environ[key]
        
        # Now re-initialize config with clean environment (JWT_SECRET still set)
        Config._instance = None
        self.config = Config.get_instance()
        self.config.initialize()
    
    def tearDown(self):
        """Restore environment variables after each test."""
        # Restore saved environment variables
        for key, value in self._saved_env.items():
            os.environ[key] = value
        # Remove JWT_SECRET test value
        if 'JWT_SECRET' in os.environ:
            del os.environ['JWT_SECRET']
        # Clear any remaining config env vars that weren't saved
        Config._instance = None

    def test_default_string_properties(self):
        for key, default in self.config.config_strings.items():
            self.assertEqual(getattr(self.config, key), default)

    def test_default_int_properties(self):
        for key, default in self.config.config_ints.items():
            self.assertEqual(getattr(self.config, key), int(default))

    def test_default_boolean_properties(self):
        for key, default in self.config.config_booleans.items():
            self.assertEqual(getattr(self.config, key), (default.lower() == "true"))

    def test_default_string_secret_properties(self):
        for key, default in self.config.config_string_secrets.items():
            if key == "JWT_SECRET":
                # JWT_SECRET is explicitly set in setUp to avoid validation error
                self.assertEqual(getattr(self.config, key), 'test-secret-for-defaults-testing')
            else:
                self.assertEqual(getattr(self.config, key), default)

    def test_default_json_secret_properties(self):
        for key, default in self.config.config_json_secrets.items():
            self.assertEqual(getattr(self.config, key), json.loads(default))

    def test_default_json_properties(self):
        for key, default in self.config.config_json_defaults.items():
            self.assertEqual(getattr(self.config, key), json.loads(default))

    def test_to_dict(self):
        """Test the to_dict method of the Config class."""
        # Convert the config object to a dictionary
        result_dict = self.config.to_dict({})
        self.assertIsInstance(result_dict["config_items"], list)
        self.assertIsInstance(result_dict["versions"], list)
        self.assertIsInstance(result_dict["enumerators"], list)
        self.assertIsInstance(result_dict["token"], dict)
        
    def test_default_string_ci(self):
        for key, default in {**self.config.config_strings, **self.config.config_ints}.items():
            self._test_config_default_value(key, default)

    def test_default_secret_ci(self):
        for key, default in {**self.config.config_string_secrets, **self.config.config_json_secrets}.items():
            if key == "JWT_SECRET":
                # JWT_SECRET is explicitly set in setUp, so it comes from environment
                items = self.config.config_items
                item = next((i for i in items if i['name'] == key), None)
                self.assertIsNotNone(item)
                self.assertEqual(item['name'], key)
                self.assertEqual(item['from'], "environment")
                self.assertEqual(item['value'], "secret")  # Still masked in config_items
            else:
                self._test_config_default_value(key, "secret")

    def test_default_json_ci(self):
        for key, default in self.config.config_json_defaults.items():
            self._test_config_default_value(key, "secret")

    def _test_config_default_value(self, config_name, expected_value):
        """Helper function to check default values."""
        items = self.config.config_items
        item = next((i for i in items if i['name'] == config_name), None)
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], config_name)
        self.assertEqual(item['from'], "default")
        self.assertEqual(item['value'], expected_value)

if __name__ == '__main__':
    unittest.main()

