"""
Service integration tests for JourneyService.

These run against the real, schema-validated MongoDB (start it with
``pipenv run db``) and exercise ``JourneyService`` through ``MongoIO`` — no HTTP
layer, since ``api_utils`` services have no REST endpoints of their own.

Philosophy (per project convention): the ``mongodb_api`` configurator owns the
schema and applies the collection validators, so the database is the authority
on stored types. We therefore assert *round-trip behavior* (string ids in ->
correct documents out) rather than re-asserting types the validator already
guarantees. A regression that stopped encoding ids/dates at the ``MongoIO``
boundary would surface here as a ``MongoIO`` write error, exactly as it would in
a running API (where ``flask_utils`` route handlers translate it to an HTTP
error).

Collaborator services (Event, Aggregation) are patched so these tests only touch
the Journey collection for a disposable test profile, which is cleaned up.
"""

import os
import unittest
from datetime import datetime, timezone
from unittest.mock import patch

import pytest
from bson import ObjectId

from api_utils import Config, MongoIO
from api_utils.services.journey_service import JourneyService, TEMPLATE_JOURNEY_ID

pytestmark = pytest.mark.integration

# Disposable profile id used only by these tests; never a real mentee.
TEST_PROFILE_ID = "eeee00000000000000009999"


class TestJourneyServiceIntegration(unittest.TestCase):
    """Exercise JourneyService mutation flows against the validated DB."""

    def setUp(self):
        Config._instance = None
        os.environ["JWT_SECRET"] = "test-secret-for-journey-integration"
        self.config = Config.get_instance()
        MongoIO._instance = None
        self.mongo = MongoIO.get_instance()

        # The lifecycle flows clone the seeded template; skip cleanly if the
        # backing data isn't present rather than reporting a false failure.
        self.template = self.mongo.get_document(
            self.config.JOURNEY_COLLECTION_NAME, TEMPLATE_JOURNEY_ID
        )
        if not self.template:
            self.skipTest("Journey template not seeded; run `pipenv run db`")

        self._delete_test_journey()
        self.token = {
            "user_id": "journey-itest",
            "roles": ["mentee", "admin"],
            "profile_id": TEST_PROFILE_ID,
        }
        self.breadcrumb = {
            "at_time": datetime.now(timezone.utc),
            "by_user": "journey-itest",
            "from_ip": "127.0.0.1",
            "correlation_id": "journey-itest-cid",
        }

    def tearDown(self):
        try:
            self._delete_test_journey()
        finally:
            self.mongo.disconnect()

    def _delete_test_journey(self):
        self.mongo.get_collection(self.config.JOURNEY_COLLECTION_NAME).delete_many(
            {"_id": ObjectId(TEST_PROFILE_ID)}
        )

    def _stored(self):
        return self.mongo.get_document(
            self.config.JOURNEY_COLLECTION_NAME, TEST_PROFILE_ID
        )

    @staticmethod
    def _first_next_resource_id(journey):
        for module in journey.get("next", []):
            for topic in module.get("topics", []):
                for rid in topic.get("resources", []):
                    return rid
        return None

    def test_get_my_journey_clones_template_into_valid_document(self):
        """get_my_journey clones the template; the write passes validation."""
        created = JourneyService.get_my_journey(self.token, self.breadcrumb)

        self.assertEqual(created["_id"], ObjectId(TEST_PROFILE_ID))
        self.assertEqual(created["profile_id"], ObjectId(TEST_PROFILE_ID))
        # It really persisted (validator accepted the encoded document).
        self.assertIsNotNone(self._stored())

    @patch("api_utils.services.aggregation_service.AggregationService.add_completion")
    @patch("api_utils.services.event_service.EventService.create_event")
    def test_advance_then_complete_round_trips(self, _mock_event, _mock_add_completion):
        """advance -> complete moves a resource next -> now -> library.

        The resource id is passed as a string (as a route would), and every
        write must satisfy the Journey schema validator.
        """
        created = JourneyService.get_my_journey(self.token, self.breadcrumb)
        rid = self._first_next_resource_id(created)
        self.assertIsNotNone(rid, "template should seed at least one next resource")

        # advance: string id in; resource lands in the now scope.
        JourneyService.advance_resource(str(rid), self.token, self.breadcrumb)
        after_advance = self._stored()
        now_ids = [item.get("resource_id") for item in after_advance.get("now", [])]
        self.assertIn(ObjectId(rid), now_ids)

        # complete: resource moves from now to library.
        JourneyService.complete_resource(
            str(rid), {"rating": 3}, self.token, self.breadcrumb
        )
        after_complete = self._stored()
        library_ids = [
            item.get("resource_id") for item in after_complete.get("library", [])
        ]
        self.assertIn(ObjectId(rid), library_ids)
        remaining_now = [
            item.get("resource_id") for item in after_complete.get("now", [])
        ]
        self.assertNotIn(ObjectId(rid), remaining_now)

    def test_promote_path_moves_later_into_next(self):
        """promote_path_to_next grows next and drops the path from later."""
        created = JourneyService.get_my_journey(self.token, self.breadcrumb)
        later = created.get("later", [])
        if not later:
            self.skipTest("template has no `later` paths to promote")

        path_id = later[0]
        next_before = len(created.get("next", []))

        JourneyService.promote_path_to_next(str(path_id), self.token, self.breadcrumb)

        stored = self._stored()
        self.assertGreater(len(stored.get("next", [])), next_before)
        self.assertNotIn(ObjectId(path_id), stored.get("later", []))


if __name__ == "__main__":
    unittest.main()
