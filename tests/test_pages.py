"""Tests for the HealthCast web pages."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def client():
    """Create a test client that triggers startup events."""
    with TestClient(app) as c:
        yield c


class TestLandingPage:
    """Tests for the landing page."""

    def test_landing_page_returns_200(self, client):
        """Landing page should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_landing_page_returns_html(self, client):
        """Landing page should return HTML content."""
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_landing_page_contains_title(self, client):
        """Landing page should contain the app title."""
        response = client.get("/")
        assert b"HealthCast" in response.content or b"Health" in response.content


class TestRecommendationsPage:
    """Tests for the recommendations page."""

    def test_recommendations_page_returns_200(self, client):
        """Recommendations page should return 200 OK."""
        response = client.get("/recommendations")
        assert response.status_code == 200

    def test_recommendations_page_returns_html(self, client):
        """Recommendations page should return HTML content."""
        response = client.get("/recommendations")
        assert "text/html" in response.headers["content-type"]

    def test_recommendations_page_contains_form(self, client):
        """Recommendations page should contain a form element."""
        response = client.get("/recommendations")
        assert b"<form" in response.content or b"form" in response.content.lower()
