import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_rss_feed():
    """Test GET /api/rss-feed returns 404 (not implemented)."""
    response = client.get("/api/rss-feed")
    assert response.status_code == 404  # Update this when endpoint is implemented

def test_get_web_feed():
    """Test GET /api/web-feed returns 404 (not implemented)."""
    response = client.get("/api/web-feed")
    assert response.status_code == 404  # Update this when endpoint is implemented 