# This file is now split into multiple files for clarity and maintainability.
# See the new files: test_health.py, test_posts.py, test_preferences.py, test_rss_web_feed.py, test_saved_content.py, and test_error_handling.py

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# ------------------- Health Endpoint -------------------
def test_health():
    """Test /health returns 200 and a status key."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()

# ------------------- Posts Endpoints -------------------
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

# ------------------- Preferences Endpoints -------------------
def test_get_preferences():
    """Test GET /api/preferences returns 200 and preferences data."""
    response = client.get("/api/preferences")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)

# def test_update_preferences():
#     """Test POST /api/preferences updates preferences with valid data."""
#     data = {"preferred_sources": ["TestSource"], "preferred_categories": ["AI"]}
#     response = client.post("/api/preferences", json=data)
#     assert response.status_code == 200
#     assert "preferred_sources" in response.json()

# ------------------- RSS & Web Feed Endpoints -------------------
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

# ------------------- Saved Content Endpoints -------------------
def test_get_saved():
    """Test GET /api/saved returns 200 and a list of saved posts."""
    response = client.get("/api/saved")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# def test_save_post():
#     """Test POST /api/saved saves a post for the user."""
#     data = {"post_id": 1}
#     response = client.post("/api/saved", json=data)
#     assert response.status_code in (200, 201)
#
# def test_delete_saved():
#     """Test DELETE /api/saved/{id} removes a saved post."""
#     response = client.delete("/api/saved/1")
#     assert response.status_code in (200, 204)

# ------------------- Error Handling & Security -------------------
def test_invalid_route():
    """Test unknown route returns 404 and error message."""
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json()

# Add more tests for authentication, authorization, and edge cases as needed. 