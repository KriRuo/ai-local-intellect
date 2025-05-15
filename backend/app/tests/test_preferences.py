# Test: /api/preferences endpoints
# - Verifies GET /api/preferences returns preferences data.
# - Limitation: Only tests GET, does not test updating preferences or error cases.
# - Recommendation: Add tests for POST, error handling, and invalid input.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

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