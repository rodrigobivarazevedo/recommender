"""Pytest configuration and shared fixtures."""

import pytest


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture(scope="session")
def test_client():
    """Create a test client that triggers startup events."""
    from fastapi.testclient import TestClient
    from app.main import app

    # Use context manager to trigger startup/shutdown events
    with TestClient(app) as client:
        yield client
