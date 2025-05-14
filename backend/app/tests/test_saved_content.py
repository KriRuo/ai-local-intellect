import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

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