"""
Unit tests for Note service.
"""

import unittest
from unittest.mock import patch, MagicMock
from bson import ObjectId
from api_utils.services.note_service import NoteService
from api_utils.flask_utils.exceptions import (
    HTTPBadRequest,
    HTTPInternalServerError,
)


class TestNoteService(unittest.TestCase):
    """Test cases for NoteService."""

    def setUp(self):
        self.mock_token = {"user_id": "test_user", "roles": ["admin"]}
        self.mock_breadcrumb = {
            "at_time": "2024-01-01T00:00:00Z",
            "by_user": "test_user",
            "from_ip": "127.0.0.1",
            "correlation_id": "test-correlation-id",
        }
        self.resource_id = "507f1f77bcf86cd799439011"

    @patch("api_utils.services.note_service.execute_list_query")
    @patch("api_utils.services.note_service.Config.get_instance")
    def test_get_notes_for_resource_success(self, mock_get_config, mock_execute_list):
        mock_config = MagicMock()
        mock_config.NOTE_COLLECTION_NAME = "Note"
        mock_get_config.return_value = mock_config
        mock_execute_list.return_value = [{"_id": "1", "note": "a"}]

        notes = NoteService.get_notes_for_resource(
            self.resource_id, self.mock_token, self.mock_breadcrumb
        )

        self.assertEqual(len(notes), 1)
        mock_execute_list.assert_called_once()
        call_kwargs = mock_execute_list.call_args[1]
        self.assertEqual(
            call_kwargs["match"]["resource_id"], ObjectId(self.resource_id)
        )

    @patch("api_utils.services.note_service.execute_list_query")
    @patch("api_utils.services.note_service.Config.get_instance")
    def test_get_notes_for_resource_invalid_id(
        self, mock_get_config, mock_execute_list
    ):
        mock_config = MagicMock()
        mock_config.NOTE_COLLECTION_NAME = "Note"
        mock_config.ROLE_ADMIN = "admin"
        mock_get_config.return_value = mock_config

        with self.assertRaises(HTTPBadRequest):
            NoteService.get_notes_for_resource(
                "invalid", self.mock_token, self.mock_breadcrumb
            )
        mock_execute_list.assert_not_called()


if __name__ == "__main__":
    unittest.main()
