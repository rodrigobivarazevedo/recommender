"""Tests for the PodcastRecommendationSystem class."""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from app.main import PodcastRecommendationSystem, recommendation_system, app


@pytest.fixture(scope="module", autouse=True)
def init_app():
    """Initialize the app to trigger startup events."""
    with TestClient(app):
        yield


class TestPodcastRecommendationSystemInit:
    """Tests for PodcastRecommendationSystem initialization."""

    def test_default_weights(self):
        """Should initialize with default weights."""
        system = PodcastRecommendationSystem()
        assert system.transcript_weight == 0.7
        assert system.metadata_weight == 0.3

    def test_custom_weights(self):
        """Should accept custom weights."""
        system = PodcastRecommendationSystem(transcript_weight=0.6, metadata_weight=0.4)
        assert system.transcript_weight == 0.6
        assert system.metadata_weight == 0.4

    def test_initial_state(self):
        """Should initialize with None values."""
        system = PodcastRecommendationSystem()
        assert system.podcast_data is None
        assert system.transcript_embeddings is None
        assert system.metadata_embeddings is None
        assert system.combined_embeddings is None
        assert system.cosine_sim is None


class TestCoseSimilarityMatrix:
    """Tests for cosine similarity calculation."""

    def test_cosine_similarity_normalized(self):
        """Should compute cosine similarity for normalized vectors."""
        system = PodcastRecommendationSystem()

        # Create normalized test vectors
        vec = np.array([1.0, 0.0, 0.0])
        matrix = np.array([
            [1.0, 0.0, 0.0],  # Same as vec
            [0.0, 1.0, 0.0],  # Orthogonal
            [0.5, 0.5, 0.0],  # 45 degrees
        ])
        # Normalize the matrix rows
        matrix = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)

        similarities = system.cosine_similarity_matrix(vec, matrix, normalized=True)

        assert len(similarities) == 3
        assert similarities[0] == pytest.approx(1.0, abs=0.01)  # Same vector
        assert similarities[1] == pytest.approx(0.0, abs=0.01)  # Orthogonal

    def test_cosine_similarity_unnormalized(self):
        """Should compute cosine similarity for unnormalized vectors."""
        system = PodcastRecommendationSystem()

        vec = np.array([2.0, 0.0, 0.0])
        matrix = np.array([
            [3.0, 0.0, 0.0],  # Same direction
            [0.0, 1.0, 0.0],  # Orthogonal
        ])

        similarities = system.cosine_similarity_matrix(vec, matrix, normalized=False)

        assert len(similarities) == 2
        assert similarities[0] == pytest.approx(1.0, abs=0.01)  # Same direction
        assert similarities[1] == pytest.approx(0.0, abs=0.01)  # Orthogonal


class TestLoadedRecommendationSystem:
    """Tests for the loaded recommendation system."""

    def test_data_loaded(self):
        """Should have podcast data loaded."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        assert len(recommendation_system.podcast_data) > 0

    def test_embeddings_prepared(self):
        """Should have embeddings prepared."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        assert recommendation_system.transcript_embeddings is not None
        assert recommendation_system.metadata_embeddings is not None
        assert recommendation_system.combined_embeddings is not None

    def test_similarity_matrix_computed(self):
        """Should have similarity matrix computed."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        assert recommendation_system.cosine_sim is not None
        # Should be square matrix
        assert recommendation_system.cosine_sim.shape[0] == recommendation_system.cosine_sim.shape[1]

    def test_embedding_model_loaded(self):
        """Should have embedding model loaded (when sentence-transformers is available)."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        # Embedding model is optional - skip if not available
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available (sentence-transformers not installed)")
        assert recommendation_system.embedding_model is not None

    def test_random_playlist_returns_data(self):
        """Random playlist should return recommendations."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        result = recommendation_system.get_random_playlist(n_recommendations=5)
        assert result is not None
        assert len(result) == 5
        assert "title" in result.columns
        assert "similarity" in result.columns

    def test_item_based_filtering(self):
        """Item-based filtering should return recommendations."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")
        result = recommendation_system.item_based_filtering("sleep", n_recommendations=3)
        if result is not None:
            assert len(result) <= 3
            assert "title" in result.columns
            assert "similarity" in result.columns

    def test_content_filtering(self):
        """Content filtering should return recommendations."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")
        result = recommendation_system.content_filtering(
            "how to improve sleep quality",
            top_n=5
        )
        assert result is not None
        assert len(result) <= 5
        assert "title" in result.columns
        assert "similarity" in result.columns

    def test_content_filtering_with_duration(self):
        """Content filtering should respect max duration."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        if recommendation_system.embedding_model is None:
            pytest.skip("Embedding model not available")
        result = recommendation_system.content_filtering(
            "meditation",
            top_n=10,
            max_min=30
        )
        if result is not None and len(result) > 0:
            assert all(result["duration_min"] <= 30)

    def test_similarity_scores_in_range(self):
        """Similarity scores should be between -1 and 1."""
        if recommendation_system.podcast_data is None:
            pytest.skip("Recommendation system not loaded")
        result = recommendation_system.get_random_playlist(n_recommendations=5)
        assert all(result["similarity"] >= -1)
        assert all(result["similarity"] <= 1)
