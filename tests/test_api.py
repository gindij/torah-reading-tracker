"""
Tests for Flask API endpoints.
"""

import json

import pytest

from backend.api.app import app


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "healthy"


def test_stats_endpoint(client):
    """Test the stats endpoint returns proper structure."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "total" in data
    assert "completed" in data
    assert "percentage" in data
    assert "aliyot" in data["total"]
    assert "words" in data["total"]
    assert "verses" in data["total"]


def test_parshiot_endpoint(client):
    """Test getting all parshiot."""
    response = client.get("/api/parshiot")
    assert response.status_code == 200
    data = json.loads(response.data)
    assert isinstance(data, list)
    if len(data) > 0:
        parsha = data[0]
        assert "title" in parsha
        assert "aliyot" in parsha
        assert isinstance(parsha["aliyot"], list)
