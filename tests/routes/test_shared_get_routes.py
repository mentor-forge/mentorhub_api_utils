import unittest
from unittest.mock import patch

from flask import Flask

from api_utils.flask_utils.exceptions import HTTPNotFound, HTTPUnauthorized
from api_utils.routes.shared_get_routes import (
    create_aggregation_get_routes,
    create_encounter_get_routes,
    create_event_get_routes,
    create_external_event_get_routes,
    create_journey_get_routes,
    create_mentee_get_routes,
    create_note_get_routes,
    create_notification_get_routes,
    create_path_get_routes,
    create_plan_get_routes,
    create_profile_get_routes,
    create_resource_get_routes,
)
from api_utils.services.resource_service import ResourceService


class FakeResourceService(ResourceService):
    """Local subclass used to prove routes dispatch through service_cls."""

    list_called = False
    get_called = False

    @classmethod
    def get_resources(cls, token, breadcrumb, offset, size, filters, sort_by):
        cls.list_called = True
        return [{"_id": "abc", "name": "one"}]

    @classmethod
    def get_resource(cls, resource_id, token, breadcrumb):
        cls.get_called = True
        if resource_id == "missing":
            raise HTTPNotFound("Resource missing not found")
        return {"_id": resource_id, "name": "doc"}


class TestSharedGetRoutes(unittest.TestCase):
    def setUp(self):
        self.mock_token = {"user_id": "user-1"}
        self.mock_breadcrumb = {
            "at_time": "2026-01-01T00:00:00Z",
            "correlation_id": "corr-1",
        }

    def _register(self, factory, service_cls, prefix):
        app = Flask(__name__)
        app.register_blueprint(factory(service_cls), url_prefix=prefix)
        return app.test_client()

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_resource_list_returns_array(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        client = self._register(
            create_resource_get_routes, ResourceService, "/api/resource"
        )

        with patch.object(
            ResourceService, "get_resources", return_value=[]
        ) as mock_get_resources:
            response = client.get("/api/resource")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        mock_get_resources.assert_called_once()

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_resource_list_one_element(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        client = self._register(
            create_resource_get_routes, ResourceService, "/api/resource"
        )
        doc = {"_id": "1", "name": "alpha"}

        with patch.object(ResourceService, "get_resources", return_value=[doc]):
            response = client.get("/api/resource")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, [doc])

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_resource_get_by_id_success(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        client = self._register(
            create_resource_get_routes, ResourceService, "/api/resource"
        )
        doc = {"_id": "rid", "name": "doc"}

        with patch.object(ResourceService, "get_resource", return_value=doc):
            response = client.get("/api/resource/rid")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, doc)
        self.assertNotIsInstance(response.json, list)

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_resource_get_by_id_not_found(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        client = self._register(
            create_resource_get_routes, ResourceService, "/api/resource"
        )

        with patch.object(
            ResourceService,
            "get_resource",
            side_effect=HTTPNotFound("Resource x not found"),
        ):
            response = client.get("/api/resource/x")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "Resource x not found"})

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_subclass_methods_are_called(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        FakeResourceService.list_called = False
        FakeResourceService.get_called = False
        client = self._register(
            create_resource_get_routes, FakeResourceService, "/api/resource"
        )

        client.get("/api/resource")
        client.get("/api/resource/ok")

        self.assertTrue(FakeResourceService.list_called)
        self.assertTrue(FakeResourceService.get_called)

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_note_list_missing_resource_id_is_400(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        from api_utils.services.note_service import NoteService

        client = self._register(create_note_get_routes, NoteService, "/api/note")
        response = client.get("/api/note")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"error": "resource_id query parameter is required"}
        )

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_note_list_with_resource_id(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        from api_utils.services.note_service import NoteService

        client = self._register(create_note_get_routes, NoteService, "/api/note")

        with patch.object(
            NoteService, "get_notes_for_resource", return_value=[]
        ) as mock_get_notes:
            response = client.get("/api/note?resource_id=507f1f77bcf86cd799439011")

        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json, list)
        mock_get_notes.assert_called_once()

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_encounter_list_missing_mentee_id_is_400(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        from api_utils.services.encounter_service import EncounterService

        client = self._register(
            create_encounter_get_routes, EncounterService, "/api/encounter"
        )
        response = client.get("/api/encounter")

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json, {"error": "mentee_id query parameter is required"}
        )

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_encounter_list_and_get_by_id(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb
        from api_utils.services.encounter_service import EncounterService

        client = self._register(
            create_encounter_get_routes, EncounterService, "/api/encounter"
        )

        with patch.object(
            EncounterService, "get_encounters_for_mentee", return_value=[{"_id": "e1"}]
        ):
            list_response = client.get("/api/encounter?mentee_id=m1")
        self.assertEqual(list_response.status_code, 200)
        self.assertIsInstance(list_response.json, list)

        with patch.object(
            EncounterService,
            "get_encounter",
            side_effect=HTTPNotFound("Encounter e2 not found"),
        ):
            get_response = client.get("/api/encounter/e2")
        self.assertEqual(get_response.status_code, 404)

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_token_failure_handled(self, mock_token, mock_breadcrumb):
        mock_token.side_effect = HTTPUnauthorized("Invalid token")
        client = self._register(
            create_resource_get_routes, ResourceService, "/api/resource"
        )

        response = client.get("/api/resource")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "Invalid token"})

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_path_plan_profile_notification_event_factories(
        self, mock_token, mock_breadcrumb
    ):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb

        from api_utils.services.event_service import EventService
        from api_utils.services.notification_service import NotificationService
        from api_utils.services.path_service import PathService
        from api_utils.services.plan_service import PlanService
        from api_utils.services.profile_service import ProfileService

        cases = [
            (create_path_get_routes, PathService, "/api/path", "get_paths", None),
            (create_plan_get_routes, PlanService, "/api/plan", "get_plans", None),
            (
                create_profile_get_routes,
                ProfileService,
                "/api/profile",
                "get_profiles",
                None,
            ),
            (
                create_notification_get_routes,
                NotificationService,
                "/api/notification",
                "get_notifications",
                None,
            ),
            (create_event_get_routes, EventService, "/api/event", "get_events", None),
        ]

        for factory, service_cls, prefix, list_method, _ in cases:
            with self.subTest(prefix=prefix):
                client = self._register(factory, service_cls, prefix)
                with patch.object(service_cls, list_method, return_value=[]):
                    response = client.get(prefix)
                self.assertEqual(response.status_code, 200)
                self.assertIsInstance(response.json, list)

    @patch("api_utils.routes.shared_get_routes.create_flask_breadcrumb")
    @patch("api_utils.routes.shared_get_routes.create_flask_token")
    def test_get_by_id_only_factories(self, mock_token, mock_breadcrumb):
        mock_token.return_value = self.mock_token
        mock_breadcrumb.return_value = self.mock_breadcrumb

        from api_utils.services.aggregation_service import AggregationService
        from api_utils.services.external_event_service import ExternalEventService
        from api_utils.services.journey_service import JourneyService
        from api_utils.services.mentee_service import MenteeService

        cases = [
            (
                create_journey_get_routes,
                JourneyService,
                "/api/journey/j1",
                "get_journey",
                {"_id": "j1"},
            ),
            (
                create_mentee_get_routes,
                MenteeService,
                "/api/mentee/p1",
                "get_mentee",
                {"_id": "p1"},
            ),
            (
                create_aggregation_get_routes,
                AggregationService,
                "/api/aggregation/r1",
                "get_aggregation_for_resource",
                {"resource_id": "r1"},
            ),
            (
                create_external_event_get_routes,
                ExternalEventService,
                "/api/external-event/ev1",
                "get_external_event",
                {"_id": "ev1"},
            ),
        ]

        for factory, service_cls, url, method_name, doc in cases:
            with self.subTest(url=url):
                prefix = url.rsplit("/", 1)[0]
                client = self._register(factory, service_cls, prefix)
                with patch.object(service_cls, method_name, return_value=doc):
                    response = client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, doc)


if __name__ == "__main__":
    unittest.main()
