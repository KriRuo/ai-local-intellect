import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_invalid_route():
    """Test unknown route returns 404 and error message."""
    response = client.get("/api/does-not-exist")
    assert response.status_code == 404
    assert "detail" in response.json() 