"""Tests for the HealthCast recommendation API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app, recommendation_system


@pytest.fixture(scope="module")
def client():
    """Create a test client that triggers startup events."""
    with TestClient(app) as c:
        yield c


class TestGetRecommendationsEndpoint:
    """Tests for the /get_recommendations endpoint."""

    def test_endpoint_exists(self, client):
        """Endpoint should exist and accept POST requests."""
        response = client.post(
            "/get_recommendations",
            data={"podcast_title": "test", "num_recommendations": 5}
        )
        # Should not return 404 or 405
        assert response.status_code in [200, 500]

    def test_requires_podcast_title(self, client):
        """Endpoint should require podcast_title field."""
        response = client.post(
            "/get_recommendations",
            data={"num_recommendations": 5}
        )
        assert response.status_code == 422  # Validation error

    def test_returns_recommendations_list(self, client):
        """Endpoint should return a recommendations list."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")

        response = client.post(
            "/get_recommendations",
            data={"podcast_title": "sleep", "num_recommendations": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_recommendation_structure(self, client):
        """Each recommendation should have required fields."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")

        response = client.post(
            "/get_recommendations",
            data={"podcast_title": "nutrition", "num_recommendations": 3}
        )
        if response.status_code == 200:
            data = response.json()
            if data["recommendations"]:
                rec = data["recommendations"][0]
                assert "title" in rec
                assert "host" in rec
                assert "duration_min" in rec
                assert "similarity_score" in rec

    def test_respects_num_recommendations(self, client):
        """Endpoint should return requested number of recommendations."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")

        response = client.post(
            "/get_recommendations",
            data={"podcast_title": "exercise", "num_recommendations": 3}
        )
        if response.status_code == 200:
            data = response.json()
            assert len(data["recommendations"]) <= 3


class TestGetRandomPlaylistEndpoint:
    """Tests for the /get_random_playlist endpoint."""

    def test_endpoint_exists(self, client):
        """Endpoint should exist and accept POST requests."""
        response = client.post(
            "/get_random_playlist",
            data={"num_recommendations": 5}
        )
        assert response.status_code in [200, 500]

    def test_returns_recommendations_list(self, client):
        """Endpoint should return a recommendations list."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")

        response = client.post(
            "/get_random_playlist",
            data={"num_recommendations": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_random_playlist_has_items(self, client):
        """Random playlist should return requested items."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")

        response = client.post(
            "/get_random_playlist",
            data={"num_recommendations": 5}
        )
        if response.status_code == 200:
            data = response.json()
            assert len(data["recommendations"]) > 0


class TestGetContentRecommendationsEndpoint:
    """Tests for the /get_content_recommendations endpoint."""

    def test_endpoint_exists(self, client):
        """Endpoint should exist and accept POST requests."""
        response = client.post(
            "/get_content_recommendations",
            data={"user_input": "test", "num_recommendations": 5}
        )
        assert response.status_code in [200, 500]

    def test_requires_user_input(self, client):
        """Endpoint should require user_input field."""
        response = client.post(
            "/get_content_recommendations",
            data={"num_recommendations": 5}
        )
        assert response.status_code == 422  # Validation error

    def test_returns_recommendations_list(self, client):
        """Endpoint should return a recommendations list."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")

        response = client.post(
            "/get_content_recommendations",
            data={"user_input": "how to improve sleep quality", "num_recommendations": 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

    def test_accepts_max_duration(self, client):
        """Endpoint should accept optional max_duration parameter."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")

        response = client.post(
            "/get_content_recommendations",
            data={
                "user_input": "meditation techniques",
                "num_recommendations": 3,
                "max_duration": 60
            }
        )
        assert response.status_code == 200

    def test_content_recommendation_structure(self, client):
        """Each content recommendation should have required fields."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")

        response = client.post(
            "/get_content_recommendations",
            data={"user_input": "stress management", "num_recommendations": 3}
        )
        if response.status_code == 200:
            data = response.json()
            if data["recommendations"]:
                rec = data["recommendations"][0]
                assert "title" in rec
                assert "host" in rec
                assert "duration_min" in rec
                assert "similarity_score" in rec
