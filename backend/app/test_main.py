import pytest
from fastapi.testclient import TestClient
from .main import app

client = TestClient(app)

def test_get_posts():
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "success"
    assert "data" in data
    assert isinstance(data["data"], list)
    if data["data"]:
        post = data["data"][0]
        assert "id" in post
        assert "title" in post
        assert "content" in post
        assert "timestamp" in post 