import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    """Test /health returns 200 and a status key."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json() 