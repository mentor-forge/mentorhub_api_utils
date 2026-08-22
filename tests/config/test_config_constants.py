import os
import unittest
from api_utils import Config


class TestConfigConstants(unittest.TestCase):

    def setUp(self):
        """Re-initialize the config for each test."""
        Config._instance = None
        os.environ["JWT_SECRET"] = "test-secret-for-constants-testing"
        self.config = Config.get_instance()

    def tearDown(self):
        if "JWT_SECRET" in os.environ:
            del os.environ["JWT_SECRET"]
        Config._instance = None

    def test_system_collection_names(self):
        self.assertEqual(self.config.ENUMERATORS_COLLECTION_NAME, "DatabaseEnumerators")
        self.assertEqual(self.config.VERSIONS_COLLECTION_NAME, "CollectionVersions")

    def test_data_collection_names(self):
        self.assertEqual(self.config.PROFILE_COLLECTION_NAME, "Profile")
        self.assertEqual(self.config.CUSTOMER_COLLECTION_NAME, "Customer")
        self.assertEqual(self.config.EVENT_COLLECTION_NAME, "Event")
        self.assertEqual(self.config.RESOURCE_COLLECTION_NAME, "Resource")
        self.assertEqual(
            self.config.RESOURCE_AGGREGATION_COLLECTION_NAME, "Resource_Aggregation"
        )
        self.assertEqual(self.config.PATH_COLLECTION_NAME, "Path")
        self.assertEqual(self.config.PLAN_COLLECTION_NAME, "Plan")
        self.assertEqual(self.config.ENCOUNTER_COLLECTION_NAME, "Encounter")
        self.assertEqual(self.config.JOURNEY_COLLECTION_NAME, "Journey")
        self.assertEqual(self.config.MENTEE_COLLECTION_NAME, "Mentee")
        self.assertEqual(self.config.RATING_COLLECTION_NAME, "Rating")
        self.assertEqual(self.config.NOTE_COLLECTION_NAME, "Note")
        self.assertEqual(self.config.EXTERNAL_EVENT_COLLECTION_NAME, "ExternalEvent")
        self.assertEqual(self.config.NOTIFICATION_COLLECTION_NAME, "Notification")
        self.assertEqual(self.config.SETTING_COLLECTION_NAME, "Setting")
        self.assertEqual(self.config.PAYMENT_COLLECTION_NAME, "Payment")

    def test_role_constants(self):
        self.assertEqual(self.config.ROLE_MENTOR, "mentor")
        self.assertEqual(self.config.ROLE_MENTEE, "mentee")
        self.assertEqual(self.config.ROLE_COORDINATOR, "coordinator")
        self.assertEqual(self.config.ROLE_CUSTOMER, "customer")
        self.assertEqual(self.config.ROLE_ADMIN, "admin")

    def test_event_type_constants(self):
        self.assertEqual(self.config.EVENT_TYPE_LOGIN, "login")
        self.assertEqual(self.config.EVENT_TYPE_LOGOUT, "logout")
        self.assertEqual(self.config.EVENT_TYPE_FAIL, "fail")
        self.assertEqual(self.config.EVENT_TYPE_ARRIVED, "arrived")
        self.assertEqual(self.config.EVENT_TYPE_COMPLETED, "completed")
        self.assertEqual(self.config.EVENT_TYPE_STARTED, "started")
        self.assertEqual(self.config.EVENT_TYPE_ENCOUNTER, "encounter")
        self.assertEqual(self.config.EVENT_TYPE_NOTE, "note")
        self.assertEqual(self.config.EVENT_TYPE_LINK, "link")
        self.assertEqual(self.config.EVENT_TYPE_ADVANCED, "advanced")

    def test_constants_not_in_config_strings(self):
        constant_names = [
            "ENUMERATORS_COLLECTION_NAME",
            "VERSIONS_COLLECTION_NAME",
            "PROFILE_COLLECTION_NAME",
            "CUSTOMER_COLLECTION_NAME",
            "EVENT_COLLECTION_NAME",
            "RESOURCE_COLLECTION_NAME",
            "RESOURCE_AGGREGATION_COLLECTION_NAME",
            "PATH_COLLECTION_NAME",
            "PLAN_COLLECTION_NAME",
            "ENCOUNTER_COLLECTION_NAME",
            "JOURNEY_COLLECTION_NAME",
            "MENTEE_COLLECTION_NAME",
            "RATING_COLLECTION_NAME",
            "NOTE_COLLECTION_NAME",
            "EXTERNAL_EVENT_COLLECTION_NAME",
            "NOTIFICATION_COLLECTION_NAME",
            "SETTING_COLLECTION_NAME",
            "PAYMENT_COLLECTION_NAME",
            "ROLE_MENTOR",
            "ROLE_MENTEE",
            "ROLE_COORDINATOR",
            "ROLE_CUSTOMER",
            "ROLE_ADMIN",
            "EVENT_TYPE_LOGIN",
            "EVENT_TYPE_LOGOUT",
            "EVENT_TYPE_FAIL",
            "EVENT_TYPE_ARRIVED",
            "EVENT_TYPE_COMPLETED",
            "EVENT_TYPE_STARTED",
            "EVENT_TYPE_ENCOUNTER",
            "EVENT_TYPE_NOTE",
            "EVENT_TYPE_LINK",
            "EVENT_TYPE_ADVANCED",
        ]
        for name in constant_names:
            self.assertNotIn(name, self.config.config_strings)

    def test_dropped_collection_names_removed(self):
        dropped_names = [
            "IDENTITY_COLLECTION_NAME",
            "LOGIN_COLLECTION_NAME",
            "CARD_COLLECTION_NAME",
            "DASHBOARD_COLLECTION_NAME",
            "SUBSCRIPTION_COLLECTION_NAME",
        ]
        for name in dropped_names:
            self.assertFalse(hasattr(self.config, name))
            self.assertNotIn(name, self.config.config_strings)

    def test_constants_survive_initialize(self):
        self.config.initialize()
        self.assertEqual(self.config.PROFILE_COLLECTION_NAME, "Profile")
        self.assertEqual(self.config.ROLE_ADMIN, "admin")
        self.assertEqual(self.config.EVENT_TYPE_LOGIN, "login")
        self.assertEqual(self.config.ENUMERATORS_COLLECTION_NAME, "DatabaseEnumerators")
        self.assertEqual(self.config.EXTERNAL_EVENT_COLLECTION_NAME, "ExternalEvent")
        self.assertEqual(self.config.NOTIFICATION_COLLECTION_NAME, "Notification")
        self.assertEqual(self.config.SETTING_COLLECTION_NAME, "Setting")
        self.assertEqual(self.config.PAYMENT_COLLECTION_NAME, "Payment")


if __name__ == "__main__":
    unittest.main()
