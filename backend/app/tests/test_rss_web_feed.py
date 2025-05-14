import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_rss_feed():
    """Test GET /api/rss-feed returns 200 and a list of items."""
    response = client.get("/api/rss-feed")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_web_feed():
    """Test GET /api/web-feed returns 200 and a list of items."""
    response = client.get("/api/web-feed")
    assert response.status_code == 200
    assert isinstance(response.json(), list) 