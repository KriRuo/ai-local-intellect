# Test: /api/posts endpoints
# - Verifies GET /api/posts (empty) and GET /api/posts/{id} (not found).
# - Limitation: Only tests empty and not found cases, does not test create, update, or delete.
# - Recommendation: Add tests for POST, PUT, DELETE, and edge cases.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_posts_empty():
    """Test GET /api/posts returns 200 and a dict with a 'data' list (empty if no posts)."""
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "data" in data
    assert isinstance(data["data"], list)

def test_get_post_not_found():
    """Test GET /api/posts/{id} returns 404 for non-existent post."""
    response = client.get("/api/posts/99999")
    assert response.status_code == 404

# Add more tests for POST, PUT, DELETE as your API supports them
# Example (uncomment and adapt if implemented):
# def test_create_post():
#     """Test POST /api/posts creates a new post with valid data."""
#     data = {"title": "Test", "content": "Test content", "url": "http://example.com"}
#     response = client.post("/api/posts", json=data)
#     assert response.status_code == 201
#     assert response.json()["title"] == "Test" 