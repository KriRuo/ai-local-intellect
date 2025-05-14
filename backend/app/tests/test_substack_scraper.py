import unittest
from backend.app.scrapers import substack_scraper
from unittest.mock import MagicMock, patch

class TestSubstackScraper(unittest.TestCase):
    """Unit tests for the substack_scraper module."""

    @patch('backend.app.scrapers.substack_scraper.requests.get')
    def test_scrape_substack_articles_success(self, mock_get):
        """Test scrape_substack_articles returns articles on valid HTML."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = '''<html><body><article><h2>Title</h2><a href='url'></a><time>2023-01-01</time><div class='author'>Author</div><div class='description'>Summary</div><img src='img.jpg'/></article></body></html>'''
        mock_get.return_value = mock_response
        articles = substack_scraper.scrape_substack_articles('http://test.com')
        self.assertIsInstance(articles, list)
        self.assertGreaterEqual(len(articles), 1)

    def test_save_substack_articles_empty(self):
        """Test save_substack_articles returns empty list if no articles."""
        mock_db = MagicMock()
        result = substack_scraper.save_substack_articles(mock_db, [])
        self.assertEqual(result, [])

if __name__ == "__main__":
    unittest.main() 