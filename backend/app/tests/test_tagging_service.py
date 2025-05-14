import unittest
from backend.app.services.tagging_service import TaggingService
from unittest.mock import MagicMock, patch

class TestTaggingService(unittest.TestCase):
    """Unit tests for the TaggingService class.
    These tests verify the integration with the OpenAI API and the correct tagging of new posts.
    Mocks are used to isolate external dependencies and database interactions.
    """

    def setUp(self):
        # Instantiate the service for each test to ensure isolation
        self.service = TaggingService()

    @patch.object(TaggingService, 'get_tags_and_category', return_value=(['AI', 'NLP'], 'AI Research'))
    def test_tag_new_posts(self, mock_get_tags):
        """
        Test that tag_new_posts processes new posts from the database:
        - Mocks the DB session and a post object.
        - Ensures set_tags is called with the expected tags.
        - Ensures the post's category is set as expected.
        - Verifies the returned stats include a successful tagging count.
        This test isolates the tagging logic from the actual OpenAI API and DB.
        """
        mock_db = MagicMock()
        mock_post = MagicMock()
        mock_post.content = "AI and NLP are cool."
        mock_post.set_tags = MagicMock()
        mock_post.category = None
        mock_db.query().filter().order_by().limit().all.return_value = [mock_post]
        stats = self.service.tag_new_posts(mock_db, batch_size=1)
        self.assertIn('successful', stats)
        self.assertGreaterEqual(stats['successful'], 1)
        mock_post.set_tags.assert_called_with(['AI', 'NLP'])
        self.assertEqual(mock_post.category, 'AI Research')

    @patch('backend.app.services.tagging_service.OpenAI')
    def test_get_tags_and_category(self, mock_openai):
        """
        Test that get_tags_and_category returns tags and category from a mocked OpenAI response:
        - Mocks the OpenAI client and its chat completion response.
        - Ensures the method parses the response and returns the correct tags and category.
        This test isolates the method from the real OpenAI API and network calls.
        """
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock(message=MagicMock(content='{"tags": ["AI", "NLP"], "category": "AI Research"}'))]
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        service = TaggingService()
        tags, category = service.get_tags_and_category("AI and NLP are cool.")
        self.assertEqual(tags, ["AI", "NLP"])
        self.assertEqual(category, "AI Research")

if __name__ == "__main__":
    unittest.main() 