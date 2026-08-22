"""
Service integration tests for JourneyService.

These run against the real, schema-validated MongoDB (start it with
``pipenv run db``) and exercise ``JourneyService`` through ``MongoIO`` — no HTTP
layer, since ``api_utils`` services have no REST endpoints of their own.
"""

import os
import unittest
from datetime import datetime, timezone

import pytest

from api_utils import Config, MongoIO
from api_utils.services.journey_service import JourneyService, TEMPLATE_JOURNEY_ID
from api_utils.flask_utils.exceptions import HTTPNotFound

pytestmark = pytest.mark.integration


class TestJourneyServiceIntegration(unittest.TestCase):
    """Exercise JourneyService consume GETs against the validated DB."""

    def setUp(self):
        Config._instance = None
        os.environ["JWT_SECRET"] = "test-secret-for-journey-integration"
        self.config = Config.get_instance()
        MongoIO._instance = None
        self.mongo = MongoIO.get_instance()

        self.template = self.mongo.get_document(
            self.config.JOURNEY_COLLECTION_NAME, TEMPLATE_JOURNEY_ID
        )
        if not self.template:
            self.skipTest("Journey template not seeded; run `pipenv run db`")

        self.token = {
            "user_id": "journey-itest",
            "roles": ["mentee", "admin"],
            "profile_id": TEMPLATE_JOURNEY_ID,
        }
        self.breadcrumb = {
            "at_time": datetime.now(timezone.utc),
            "by_user": "journey-itest",
            "from_ip": "127.0.0.1",
            "correlation_id": "journey-itest-cid",
        }

    def tearDown(self):
        self.mongo.disconnect()

    def test_get_journey_returns_seeded_template(self):
        """get_journey returns an existing document by id without cloning."""
        journey = JourneyService.get_journey(
            TEMPLATE_JOURNEY_ID, self.token, self.breadcrumb
        )

        self.assertEqual(str(journey["_id"]), TEMPLATE_JOURNEY_ID)

    def test_get_journey_not_found_for_missing_id(self):
        """get_journey raises HTTPNotFound when the document does not exist."""
        missing_id = "eeee00000000000000009999"
        with self.assertRaises(HTTPNotFound):
            JourneyService.get_journey(missing_id, self.token, self.breadcrumb)


if __name__ == "__main__":
    unittest.main()
