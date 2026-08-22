"""
E2E tests for demo-server consume GET routes.

Black-box tests against ``pipenv run dev`` at localhost:8385 (COMMON_CODE_API_PORT).
"""

import pytest

from tests.e2e_auth import get_auth_token

BASE_URL = "http://localhost:8385"

# Well-formed 24-hex MongoDB ObjectId unlikely to exist in the backing DB.
UNKNOWN_OBJECT_ID = "507f1f77bcf86cd799439011"

LIST_PREFIXES = [
    "/api/resource",
    "/api/path",
    "/api/plan",
    "/api/profile",
    "/api/notification",
    "/api/event",
]

LIST_WITH_GET_BY_ID_PREFIXES = [
    "/api/resource",
    "/api/path",
    "/api/plan",
    "/api/profile",
]

ITEM_ONLY_PREFIXES = [
    "/api/journey",
    "/api/mentee",
    "/api/aggregation",
    "/api/external-event",
]

ITEM_ONLY_NOT_FOUND_PREFIXES = [
    "/api/journey",
    "/api/mentee",
    "/api/external-event",
]

_CURSOR_KEYS = frozenset({"items", "has_more", "next_cursor"})


def _requests():
    """Import lazily so ``pytest -m "not e2e"`` collection does not require dev-only ``requests``."""
    import requests

    return requests


def _auth_headers():
    token = get_auth_token()
    return {"Authorization": f"Bearer {token}"}


def _assert_json_list(body, prefix):
    """List endpoints must return a JSON array, not a cursor envelope."""
    if isinstance(body, dict):
        found = _CURSOR_KEYS.intersection(body.keys())
        assert (
            not found
        ), f"{prefix} returned cursor-style dict with keys {sorted(found)}"
    assert isinstance(
        body, list
    ), f"{prefix} list should return JSON array, got {type(body).__name__}"


@pytest.mark.e2e
@pytest.mark.parametrize("prefix", LIST_PREFIXES)
def test_list_returns_401_without_token(prefix):
    response = _requests().get(f"{BASE_URL}{prefix}")
    assert (
        response.status_code == 401
    ), f"{prefix}: expected 401, got {response.status_code}"


@pytest.mark.e2e
@pytest.mark.parametrize("prefix", LIST_PREFIXES)
def test_list_returns_array_with_token(prefix):
    response = _requests().get(f"{BASE_URL}{prefix}", headers=_auth_headers())
    assert (
        response.status_code == 200
    ), f"{prefix}: expected 200, got {response.status_code}"
    _assert_json_list(response.json(), prefix)


@pytest.mark.e2e
@pytest.mark.parametrize("prefix", LIST_PREFIXES)
def test_list_respects_size_header(prefix):
    headers = {**_auth_headers(), "offset": "0", "size": "1"}
    response = _requests().get(f"{BASE_URL}{prefix}", headers=headers)
    assert (
        response.status_code == 200
    ), f"{prefix}: expected 200, got {response.status_code}"
    body = response.json()
    _assert_json_list(body, prefix)
    assert (
        len(body) <= 1
    ), f"{prefix}: expected at most 1 item with size=1, got {len(body)}"


@pytest.mark.e2e
@pytest.mark.parametrize("prefix", LIST_WITH_GET_BY_ID_PREFIXES)
def test_get_by_id_unknown_returns_404(prefix):
    url = f"{BASE_URL}{prefix}/{UNKNOWN_OBJECT_ID}"
    response = _requests().get(url, headers=_auth_headers())
    assert (
        response.status_code == 404
    ), f"{url}: expected 404, got {response.status_code}"


@pytest.mark.e2e
def test_note_list_missing_resource_id_returns_400():
    response = _requests().get(f"{BASE_URL}/api/note", headers=_auth_headers())
    assert response.status_code == 400, f"expected 400, got {response.status_code}"


@pytest.mark.e2e
def test_note_list_with_resource_id_returns_array():
    url = f"{BASE_URL}/api/note?resource_id={UNKNOWN_OBJECT_ID}"
    response = _requests().get(url, headers=_auth_headers())
    assert response.status_code == 200, f"expected 200, got {response.status_code}"
    _assert_json_list(response.json(), "/api/note")


@pytest.mark.e2e
def test_encounter_list_missing_mentee_id_returns_400():
    response = _requests().get(f"{BASE_URL}/api/encounter", headers=_auth_headers())
    assert response.status_code == 400, f"expected 400, got {response.status_code}"


@pytest.mark.e2e
def test_encounter_list_with_mentee_id_returns_array():
    url = f"{BASE_URL}/api/encounter?mentee_id={UNKNOWN_OBJECT_ID}"
    response = _requests().get(url, headers=_auth_headers())
    assert response.status_code == 200, f"expected 200, got {response.status_code}"
    _assert_json_list(response.json(), "/api/encounter")


@pytest.mark.e2e
@pytest.mark.parametrize("prefix", ITEM_ONLY_PREFIXES)
def test_item_only_returns_401_without_token(prefix):
    url = f"{BASE_URL}{prefix}/{UNKNOWN_OBJECT_ID}"
    response = _requests().get(url)
    assert (
        response.status_code == 401
    ), f"{url}: expected 401, got {response.status_code}"


@pytest.mark.e2e
@pytest.mark.parametrize("prefix", ITEM_ONLY_NOT_FOUND_PREFIXES)
def test_item_only_unknown_id_returns_404(prefix):
    url = f"{BASE_URL}{prefix}/{UNKNOWN_OBJECT_ID}"
    response = _requests().get(url, headers=_auth_headers())
    assert (
        response.status_code == 404
    ), f"{url}: expected 404, got {response.status_code}"


@pytest.mark.e2e
def test_aggregation_unknown_resource_id_returns_null():
    """Aggregation hides missing or invisible resources as ``200`` + ``null`` (R082)."""
    url = f"{BASE_URL}/api/aggregation/{UNKNOWN_OBJECT_ID}"
    response = _requests().get(url, headers=_auth_headers())
    assert (
        response.status_code == 200
    ), f"{url}: expected 200, got {response.status_code}"
    assert response.json() is None, f"{url}: expected null body for unknown resource"
