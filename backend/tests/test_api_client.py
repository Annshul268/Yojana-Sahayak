"""Test frontend API client against backend app."""

from unittest.mock import MagicMock, patch
from frontend.services.api_client import APIClient


def test_api_client_health_success():
    """Verify frontend APIClient processes healthy backend response."""
    client = APIClient(base_url="http://localhost:8000")

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "status": "healthy",
        "service": "Yojana Sahayak",
        "version": "0.1.0",
        "environment": "development",
        "timestamp": "2026-09-21T06:50:00.000000+00:00",
    }

    with patch("httpx.Client.get", return_value=mock_resp):
        result = client.check_health()
        assert result["ok"] is True
        assert result["status_code"] == 200
        assert result["data"]["status"] == "healthy"
        assert result["data"]["service"] == "Yojana Sahayak"


def test_api_client_health_connection_error():
    """Verify frontend APIClient cleanly handles connection failure."""
    import httpx

    client = APIClient(base_url="http://localhost:8000")

    with patch("httpx.Client.get", side_effect=httpx.ConnectError("Connection refused")):
        result = client.check_health()
        assert result["ok"] is False
        assert result["status_code"] is None
        assert "Unable to connect" in result["error"]
