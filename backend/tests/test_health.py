"""Test health check and root endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    """Verify GET /api/health returns 200 and status 'healthy'."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Yojana Sahayak"
        assert "version" in data
        assert "timestamp" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Verify GET / returns 200 with service metadata."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert data["name"] == "Yojana Sahayak"
        assert data["health"] == "/api/health"
