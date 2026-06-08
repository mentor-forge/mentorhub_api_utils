import unittest
import os
from api_utils import Config

class TestConfigEnvironment(unittest.TestCase):

    def setUp(self):
        """Re-initialize the config for each test."""
        Config._instance = None
        # Set JWT_SECRET first (before getting instance) to avoid validation error
        os.environ['JWT_SECRET'] = 'ENV_VALUE'
        
        self.config = Config.get_instance()
        
        # Set all environment variables to "ENV_VALUE"
        for key, default in {**self.config.config_strings, **self.config.config_string_secrets}.items():
            if key != "BUILT_AT" and key != "CONFIG_FOLDER":
                os.environ[key] = "ENV_VALUE"
            
        for key, default in self.config.config_ints.items():
            os.environ[key] = "1234"

        for key, default in self.config.config_booleans.items():
            os.environ[key] = "true"

        for key, default in self.config.config_json_secrets.items():
            os.environ[key] = '{"foo":"bar"}'

        for key, default in self.config.config_json_defaults.items():
            os.environ[key] = '{"foo":"bar"}'

        # Initialize the Config object
        self.config.initialize()
        
        # Reset environment variables 
        for key, default in {**self.config.config_strings, **self.config.config_ints, **self.config.config_string_secrets, **self.config.config_json_secrets, **self.config.config_json_defaults}.items():
            if key != "BUILT_AT" and key != "CONFIG_FOLDER":
                if key in os.environ:
                    del os.environ[key]
            
    def test_env_string_properties(self):
        for key, default in {**self.config.config_strings, **self.config.config_string_secrets}.items():
            if key != "BUILT_AT" and key != "CONFIG_FOLDER":
                self.assertEqual(getattr(self.config, key), "ENV_VALUE")

    def test_env_int_properties(self):
        for key, default in self.config.config_ints.items():
            self.assertEqual(getattr(self.config, key), 1234)

    def test_env_boolean_properties(self):
        for key, default in self.config.config_booleans.items():
            self.assertEqual(getattr(self.config, key), True)
            
    def test_env_json_secret_properties(self):
        for key, default in self.config.config_json_secrets.items():
            self.assertEqual(getattr(self.config, key), {"foo":"bar"})
            
    def test_env_json_default_properties(self):
        for key, default in self.config.config_json_defaults.items():
            self.assertEqual(getattr(self.config, key), {"foo":"bar"})

    def test_env_string_ci(self):
        for key, default in self.config.config_strings.items():
            if key != "BUILT_AT" and key != "CONFIG_FOLDER":
                self._test_config_environment_value(key, "ENV_VALUE")

    def test_env_int_ci(self):
        for key, default in self.config.config_ints.items():
            self._test_config_environment_value(key, "1234")

    def test_env_secret_ci(self):
        for key, default in {**self.config.config_string_secrets, **self.config.config_json_secrets, **self.config.config_json_defaults}.items():
            self._test_config_environment_value(key, "secret")

    def _test_config_environment_value(self, ci_name, value):
        """Helper function to check environment values."""
        items = self.config.config_items
        item = next((i for i in items if i['name'] == ci_name), None)
        self.assertIsNotNone(item)
        self.assertEqual(item['name'], ci_name)
        self.assertEqual(item['value'], value)
        self.assertEqual(item['from'], "environment")

if __name__ == '__main__':
    unittest.main()

