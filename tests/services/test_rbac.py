"""
Unit tests for outbound RBAC match helpers.
"""

import unittest
from unittest.mock import patch

from bson import ObjectId

from api_utils.flask_utils.exceptions import HTTPNotFound
from api_utils.services.rbac import (
    EMPTY_SCOPE_MATCH,
    and_match,
    build_outbound_match,
    is_admin,
    matches_outbound,
    require_outbound,
)


class TestIsAdmin(unittest.TestCase):
    @patch("api_utils.services.rbac.Config.get_instance")
    def test_is_admin_true(self, mock_get_config):
        mock_get_config.return_value.ROLE_ADMIN = "admin"
        self.assertTrue(is_admin({"roles": ["developer", "admin"]}))

    @patch("api_utils.services.rbac.Config.get_instance")
    def test_is_admin_false(self, mock_get_config):
        mock_get_config.return_value.ROLE_ADMIN = "admin"
        self.assertFalse(is_admin({"roles": ["developer"]}))


class TestBuildOutboundMatch(unittest.TestCase):
    @patch("api_utils.services.rbac.Config.get_instance")
    def test_admin_is_unrestricted(self, mock_get_config):
        mock_get_config.return_value.ROLE_ADMIN = "admin"
        token = {"roles": ["admin"]}
        clauses = [{"status": {"$ne": "archived"}}, {"$or": [{"profile_id": "p1"}]}]
        self.assertEqual(build_outbound_match(token, clauses), {})

    @patch("api_utils.services.rbac.Config.get_instance")
    def test_non_admin_and_clauses(self, mock_get_config):
        mock_get_config.return_value.ROLE_ADMIN = "admin"
        token = {"roles": ["mentee"]}
        archived = {"status": {"$ne": "archived"}}
        identity = {
            "$or": [
                {"profile_id": "profile-1"},
                {"customer_id": "customer-1"},
            ]
        }
        match = build_outbound_match(token, [archived, identity])
        self.assertEqual(
            match,
            {
                "status": {"$ne": "archived"},
                "$or": [
                    {"profile_id": "profile-1"},
                    {"customer_id": "customer-1"},
                ],
            },
        )

    @patch("api_utils.services.rbac.Config.get_instance")
    def test_empty_scope_does_not_fall_open(self, mock_get_config):
        mock_get_config.return_value.ROLE_ADMIN = "admin"
        token = {"roles": ["mentee"]}
        match = build_outbound_match(
            token,
            [{"status": {"$ne": "archived"}}, EMPTY_SCOPE_MATCH],
        )
        self.assertEqual(match["status"], {"$ne": "archived"})
        self.assertEqual(match["_id"], {"$in": []})
        doc = {"_id": ObjectId(), "status": "active", "profile_id": "anyone"}
        self.assertFalse(matches_outbound(doc, match))


class TestAndMatch(unittest.TestCase):
    def test_merges_non_colliding_keys(self):
        base = {"status": {"$ne": "archived"}}
        search = {"name": {"$regex": "alpha", "$options": "i"}}
        self.assertEqual(
            and_match(base, search),
            {
                "status": {"$ne": "archived"},
                "name": {"$regex": "alpha", "$options": "i"},
            },
        )

    def test_wraps_colliding_status_keys(self):
        base = {"status": {"$ne": "archived"}}
        search = {"status": {"$in": ["active"]}}
        self.assertEqual(
            and_match(base, search),
            {
                "$and": [
                    {"status": {"$ne": "archived"}},
                    {"status": {"$in": ["active"]}},
                ]
            },
        )


class TestMatchesOutbound(unittest.TestCase):
    def test_archived_clause_excludes_archived(self):
        match = {"status": {"$ne": "archived"}}
        self.assertTrue(matches_outbound({"status": "active"}, match))
        self.assertFalse(matches_outbound({"status": "archived"}, match))

    def test_or_identity_clauses(self):
        match = {
            "$or": [
                {"profile_id": "profile-1"},
                {"customer_id": "customer-1"},
            ]
        }
        self.assertTrue(matches_outbound({"profile_id": "profile-1"}, match))
        self.assertTrue(matches_outbound({"customer_id": "customer-1"}, match))
        self.assertFalse(matches_outbound({"profile_id": "other"}, match))

    def test_global_exists(self):
        match = {"$or": [{"profile_id": "p1"}, {"global": {"$exists": True}}]}
        self.assertTrue(matches_outbound({"global": True}, match))
        self.assertFalse(matches_outbound({"profile_id": "other"}, match))

    def test_and_with_search_status(self):
        match = and_match(
            {"status": {"$ne": "archived"}},
            {"status": {"$in": ["active"]}},
        )
        self.assertTrue(matches_outbound({"status": "active"}, match))
        self.assertFalse(matches_outbound({"status": "archived"}, match))
        self.assertFalse(matches_outbound({"status": "draft"}, match))


class TestRequireOutbound(unittest.TestCase):
    def test_raises_not_found_for_none(self):
        with self.assertRaises(HTTPNotFound):
            require_outbound(None, {"status": {"$ne": "archived"}})

    def test_raises_not_found_for_mismatch(self):
        doc = {"_id": "123", "status": "archived"}
        match = {"status": {"$ne": "archived"}}
        with self.assertRaises(HTTPNotFound) as context:
            require_outbound(doc, match, not_found_message="Resource 123 not found")
        self.assertIn("123", str(context.exception))

    def test_returns_document_on_match(self):
        doc = {"_id": "123", "status": "active"}
        match = {"status": {"$ne": "archived"}}
        self.assertIs(require_outbound(doc, match), doc)


if __name__ == "__main__":
    unittest.main()
