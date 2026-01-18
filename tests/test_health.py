"""Tests for the HealthCast API health endpoint."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client that triggers startup events."""
    with TestClient(app) as c:
        yield c


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_returns_200(self, client):
        """Health endpoint should return 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_status(self, client):
        """Health endpoint should return status field."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"

    def test_health_includes_system_status(self, client):
        """Health endpoint should indicate if recommendation system is loaded."""
        response = client.get("/health")
        data = response.json()
        assert "recommendation_system_loaded" in data
        assert isinstance(data["recommendation_system_loaded"], bool)
