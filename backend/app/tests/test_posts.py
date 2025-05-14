import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_get_posts_empty():
    """Test GET /api/posts returns 200 and a list (empty if no posts)."""
    response = client.get("/api/posts")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

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