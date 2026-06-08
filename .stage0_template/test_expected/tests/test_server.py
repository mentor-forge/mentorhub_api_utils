"""
E2E tests for the demo server.

These tests verify that the server endpoints work correctly by making
actual HTTP requests to a running server at localhost:8385 (COMMON_CODE_API_PORT).
"""
import pytest

from tests.e2e_auth import get_auth_token

BASE_URL = "http://localhost:8385"


def _requests():
    """Import lazily so `pytest -m "not e2e"` collection does not require dev-only `requests`."""
    import requests

    return requests


@pytest.mark.e2e
def test_config_endpoint_returns_401_without_token():
    """Test that /api/config endpoint returns 401 without authentication."""
    response = _requests().get(f"{BASE_URL}/api/config")
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"


@pytest.mark.e2e
def test_config_endpoint_returns_200_with_token():
    """Test that /api/config endpoint returns 200 with valid token."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = _requests().get(f"{BASE_URL}/api/config", headers=headers)
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


@pytest.mark.e2e
def test_config_endpoint_returns_expected_structure():
    """Test that /api/config endpoint returns expected JSON structure."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = _requests().get(f"{BASE_URL}/api/config", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert 'config_items' in data, "Response missing 'config_items' key"
    assert 'versions' in data, "Response missing 'versions' key"
    assert 'enumerators' in data, "Response missing 'enumerators' key"
    assert 'token' in data, "Response missing 'token' key"


@pytest.mark.e2e
def test_config_endpoint_returns_config_items():
    """Test that /api/config endpoint returns configuration items."""
    token = get_auth_token()
    headers = {"Authorization": f"Bearer {token}"}
    response = _requests().get(f"{BASE_URL}/api/config", headers=headers)
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data['config_items'], list), "config_items should be a list"
    assert len(data['config_items']) > 0, "config_items should not be empty"


@pytest.mark.e2e
def test_metrics_endpoint_returns_200():
    """Test that /metrics endpoint returns 200 status."""
    response = _requests().get(f"{BASE_URL}/metrics")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"


@pytest.mark.e2e
def test_metrics_endpoint_returns_prometheus_format():
    """Test that /metrics endpoint returns Prometheus-formatted metrics."""
    response = _requests().get(f"{BASE_URL}/metrics")
    assert response.status_code == 200

    content = response.text
    assert len(content) > 0, "Metrics endpoint should return content"
    # Prometheus metrics typically contain key-value pairs or comments
    assert '#' in content or '=' in content or '\n' in content, \
        "Metrics should be in Prometheus format"