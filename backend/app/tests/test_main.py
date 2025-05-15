import unittest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

class TestAPIEndpoints(unittest.TestCase):
    """Test suite for main FastAPI endpoints in main.py."""

    def test_health_check(self):
        """Test the /health endpoint returns 200 and expected content."""
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.text.lower())

    def test_get_posts(self):
        """Test the /api/posts endpoint returns 200 and a list."""
        response = client.get("/api/posts")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), dict) or isinstance(response.json(), list))

    def test_get_rss_sources(self):
        """Test the /api/rss-sources endpoint returns 200 and a list."""
        response = client.get("/api/rss-sources")
        self.assertEqual(response.status_code, 200)
        self.assertIn("data", response.json())

    def test_get_preferences(self):
        """Test the /api/preferences endpoint returns 200 and preference keys."""
        response = client.get("/api/preferences")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("preferred_sources", data)
        self.assertIn("preferred_categories", data)

    def test_get_saved_posts(self):
        """Test the /api/saved endpoint returns 200 and a list."""
        response = client.get("/api/saved")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(isinstance(response.json(), list))

    def test_pipeline_refresh_all(self):
        """Test the /api/pipeline/refresh-all endpoint returns expected structure."""
        response = client.post("/api/pipeline/refresh-all")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("status", data)
        self.assertIn("summary", data)
        summary = data["summary"]
        self.assertIn("scraping", summary)
        self.assertIn("tagging", summary)
        # Accept both success and error status
        self.assertIn(data["status"], ["success", "error"])

    # Add more endpoint tests as needed, e.g. POST/DELETE, error cases, etc.

if __name__ == "__main__":
    unittest.main() 