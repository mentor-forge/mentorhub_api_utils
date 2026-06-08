"""
Configuration management module for api_utils.

This module provides a singleton Config class that manages application configuration
with support for multiple configuration sources (files, environment variables, defaults)
and automatic type conversion (strings, integers, booleans, JSON).
"""
import os
import json
from pathlib import Path

import logging
logger = logging.getLogger(__name__)

class Config:
    """
    Singleton configuration manager for the application.
    
    The Config class provides centralized configuration management with a priority
    system for configuration sources:
    1. Configuration files (in CONFIG_FOLDER directory)
    2. Environment variables
    3. Default values (defined in class)
    
    Configuration values are automatically typed based on their category:
    - Strings: Plain text values
    - Integers: Numeric port numbers and similar values
    - Booleans: True/false flags
    - JSON: Complex structured data (parsed from JSON strings)
    
    Secret values are masked in the config_items tracking list to prevent
    accidental exposure in logs or API responses.
    
    Attributes:
        _instance (Config): The singleton instance of the Config class.
        config_items (list): List of dictionaries tracking each config value's
            source and value (secrets are masked).
        versions (list): List of version information documents.
        enumerators (list): List of enumerator documents from MongoDB.
    
    Example:
        >>> config = Config.get_instance()
        >>> print(config.MONGO_DB_NAME)
        'engagement'
        >>> print(config.MONGODB_API_PORT)
        8180
        >>> print(config.IDENTITY_COLLECTION_NAME)
        'Identity'
        >>> print(config.DASHBOARD_API_PORT)
        8186
    """
    _instance = None  # Singleton instance

    def __init__(self):
        """
        Initialize the Config singleton instance.
        
        Raises:
            Exception: If an instance already exists (singleton pattern enforcement).
        
        Note:
            This constructor should not be called directly. Use get_instance() instead.
        """
        if Config._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config._instance = self
            self.config_items = []
            self.versions = []
            self.enumerators = []
            
            # Declare instance variables to support IDE code assist
            self.BUILT_AT = ''
            self.CONFIG_FOLDER = ''
            self.LOGGING_LEVEL = ''

            # JWT Configuration
            self.JWT_SECRET = ''
            self.JWT_ALGORITHM = ''
            self.JWT_ISSUER = ''
            self.JWT_AUDIENCE = ''
    
            # MongoDB Backing Service Configuration
            self.MONGO_DB_NAME = ''
            self.MONGO_CONNECTION_STRING = ''

            # Batch Processing Configuration
            self.INPUT_FOLDER = ''
            self.OUTPUT_FOLDER = ''

            # System Collection Names
            self.ENUMERATORS_COLLECTION_NAME = ''
            self.VERSIONS_COLLECTION_NAME = ''

            # Data collection names (from catalog.data_dictionaries)
            self.IDENTITY_COLLECTION_NAME = ''
            self.PROFILE_COLLECTION_NAME = ''
            self.CONTROL_COLLECTION_NAME = ''
            self.CREATE_COLLECTION_NAME = ''
            self.CONSUME_COLLECTION_NAME = ''

            # Service Port numbers (defaults from specifications.architecture domains)
            self.SCHEMA_API_PORT = 0
            self.SCHEMA_SPA_PORT = 0
            self.COMMON_CODE_API_PORT = 0
            self.COMMON_CODE_SPA_PORT = 0
            self.PROFILE_API_PORT = 0
            self.PROFILE_SPA_PORT = 0
            self.MENTOR_API_PORT = 0
            self.MENTOR_SPA_PORT = 0
            self.MEMBER_API_PORT = 0
            self.MEMBER_SPA_PORT = 0


            # Default Values grouped by value type            
            self.config_strings = {
                "BUILT_AT": "LOCAL",
                "CONFIG_FOLDER": "./",
                "INPUT_FOLDER": "/input",
                "OUTPUT_FOLDER": "/output",
                "LOGGING_LEVEL": "INFO", 
                "MONGO_DB_NAME": "mentor_hub",
                
                # JWT Configuration
                "JWT_ALGORITHM": "HS256",
                "JWT_ISSUER": "dev-idp",
                "JWT_AUDIENCE": "dev-api",

                # System Collection Names
                "ENUMERATORS_COLLECTION_NAME": "DatabaseEnumerators",
                "VERSIONS_COLLECTION_NAME": "CollectionVersions",
                
                # Data collection names (from catalog.data_dictionaries)
                "IDENTITY_COLLECTION_NAME": "Identity",
                "PROFILE_COLLECTION_NAME": "Profile",
                "CONTROL_COLLECTION_NAME": "Control",
                "CREATE_COLLECTION_NAME": "Create",
                "CONSUME_COLLECTION_NAME": "Consume",
            }
            self.config_ints = {
                # Service Port numbers (from specifications.architecture domain repos)
                "SCHEMA_API_PORT": 8383,
                "SCHEMA_SPA_PORT": 8384,
                "COMMON_CODE_API_PORT": 8385,
                "COMMON_CODE_SPA_PORT": 8386,
                "PROFILE_API_PORT": 8387,
                "PROFILE_SPA_PORT": 8388,
                "MENTOR_API_PORT": 8389,
                "MENTOR_SPA_PORT": 8390,
                "MEMBER_API_PORT": 8391,
                "MEMBER_SPA_PORT": 8392,
            }

            self.config_booleans = {
            }

            self.config_json_defaults = {
            }            

            self.config_string_secrets = {  
                "MONGO_CONNECTION_STRING": "mongodb://mongodb:27017",
                "JWT_SECRET": "dev-secret-change-me"
            }
            
            self.config_json_secrets = {
            }

            # Initialize configuration
            self.initialize()
            self.configure_logging()

    def initialize(self):
        """
        Initialize or re-initialize all configuration values.
        
        This method loads configuration values from files, environment variables,
        or defaults (in that priority order) and sets them as instance attributes.
        It also resets the config_items, versions, and enumerators lists.
        
        The method processes configuration in the following order:
        1. String configurations
        2. Integer configurations (converted to int)
        3. Boolean configurations (converted from "true"/"false" strings)
        4. JSON default configurations (parsed from JSON strings)
        5. String secret configurations
        6. JSON secret configurations (parsed from JSON strings)
        
        Each configuration value is tracked in config_items with its source
        (file, environment, or default) and value (secrets are masked).
        """
        self.config_items = []
        self.versions = []
        self.enumerators = []

        # Initialize Config Strings
        for key, default in self.config_strings.items():
            value = self._get_config_value(key, default, False)
            setattr(self, key, value)
            
        # Initialize Config Integers
        for key, default in self.config_ints.items():
            value = int(self._get_config_value(key, default, False))
            setattr(self, key, value)
            
        # Initialize Config Booleans
        for key, default in self.config_booleans.items():
            value = (self._get_config_value(key, default, False)).lower() == "true"
            setattr(self, key, value)
            
        # Initialize Config JSON
        for key, default in self.config_json_defaults.items():
            value = json.loads(self._get_config_value(key, default, True))
            setattr(self, key, value)
            
        # Initialize String Secrets
        for key, default in self.config_string_secrets.items():
            value = self._get_config_value(key, default, True)
            
            # Special handling for JWT_SECRET: fail fast if default is used
            if key == "JWT_SECRET" and value == default:
                error_msg = (
                    "JWT_SECRET must be explicitly set. Using the default value is not allowed for security reasons. "
                    "Please set JWT_SECRET environment variable to a secure random value."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            setattr(self, key, value)

        # Initialize JSON Secrets
        for key, default in self.config_json_secrets.items():
            value = json.loads(self._get_config_value(key, default, True))
            setattr(self, key, value)
            
        return

    def configure_logging(self):
        """
        Configure Python logging based on the LOGGING_LEVEL configuration.
        
        This method:
        - Validates and sets the logging level from LOGGING_LEVEL config
        - Resets all existing logging handlers
        - Configures basic logging with a standard format
        - Suppresses noisy HTTP-related loggers (httpcore, httpx)
        - Logs the initialized configuration items
        
        The logging format includes timestamp, level, logger name, and message.
        """
        # Make sure we have a valid logging level
        self.LOGGING_LEVEL = getattr(logging, self.LOGGING_LEVEL, logging.INFO)
        
        # Reset logging handlers
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configure logger
        logging.basicConfig(
            level=self.LOGGING_LEVEL,
            format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # Suppress noisy http logging
        logging.getLogger("httpcore").setLevel(logging.WARNING)  
        logging.getLogger("httpx").setLevel(logging.WARNING)  

        # Log configuration
        logger.info(f"Configuration Initialized: {self.config_items}")
        
        return
            
    def _get_config_value(self, name, default_value, is_secret):
        """
        Retrieve a configuration value using the priority system.
        
        Configuration sources are checked in this order:
        1. Configuration file: {CONFIG_FOLDER}/{name}
        2. Environment variable: {name}
        3. Default value: {default_value}
        
        Args:
            name (str): The name of the configuration key.
            default_value (str): The default value to use if not found in file or env.
            is_secret (bool): If True, the value will be masked as "secret" in
                config_items tracking.
        
        Returns:
            str: The configuration value as a string (may need type conversion
                by the caller).
        
        Note:
            The source and value (masked if secret) are recorded in config_items
            for tracking and debugging purposes.
        """
        value = default_value
        from_source = "default"

        # Check for config file first
        file_path = Path(self.CONFIG_FOLDER) / name
        if file_path.exists():
            value = file_path.read_text().strip()
            from_source = "file"
            
        # If no file, check for environment variable
        elif os.getenv(name):
            value = os.getenv(name)
            from_source = "environment"

        # Record the source of the config value
        self.config_items.append({
            "name": name,
            "value": "secret" if is_secret else value,
            "from": from_source
        })
        return value

    def set_enumerators(self, enumerations):
        """
        Set the enumerators list from MongoDB.
        
        Args:
            enumerations (list or iterable): The enumerator documents to store.
                If not a list, it will be converted to one.
        
        Returns:
            None
        """
        self.enumerators = enumerations if isinstance(enumerations, list) else list(enumerations)
        return
    
    def set_versions(self, versions):
        """
        Set the versions list from MongoDB.
        
        Args:
            versions (list or iterable): The version documents to store.
                If not a list, it will be converted to one.
        
        Returns:
            None
        """
        self.versions = versions if isinstance(versions, list) else list(versions)
        return
    
    def to_dict(self, token):
        """
        Convert the Config object to a dictionary for JSON serialization.
        
        This method is typically used to expose configuration via API endpoints.
        Secret values in config_items are already masked (showing "secret" instead
        of actual values).
        
        Args:
            token (dict): Authentication/authorization token to include in the response.
        
        Returns:
            dict: A dictionary containing:
                - config_items (list): List of configuration items with source tracking
                - versions (list): Version information documents
                - enumerators (list): Enumerator documents
                - token (dict): The provided token
        """
        return {
            "config_items": self.config_items,
            "versions": self.versions,
            "enumerators": self.enumerators,
            "token": token
        }    

    @staticmethod
    def get_instance():
        """
        Get the singleton instance of the Config class.
        
        This is the preferred way to access the Config instance. If no instance
        exists, one will be created automatically.
        
        Returns:
            Config: The singleton Config instance.
        
        Example:
            >>> config = Config.get_instance()
            >>> db_name = config.MONGO_DB_NAME
        """
        if Config._instance is None:
            Config()
            
        # logger.log("Config Initializing")
        return Config._instance
