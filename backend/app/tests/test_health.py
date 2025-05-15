# Test: /health endpoint
# - Verifies the /health endpoint returns 200 and a status key.
# - Limitation: Only checks for successful response, does not test error or degraded health scenarios.
# - Recommendation: Add tests for error states and health degradation.
import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health():
    """Test /health returns 200 and a status key."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json() 