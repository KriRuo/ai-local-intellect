import unittest
from backend.app.scrapers import lmarena_scraper
from unittest.mock import MagicMock

class TestLmarenaScraper(unittest.TestCase):
    """Unit tests for the lmarena_scraper module."""

    def test_scrape_lmarena_blog_success(self):
        """Test scrape_lmarena_blog returns posts on valid scrape."""
        mock_page = MagicMock()
        mock_page.goto = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[MagicMock(get_attribute=MagicMock(return_value='/blog/test'))])
        mock_page.query_selector = MagicMock(return_value=MagicMock(inner_text=lambda: 'Title'))
        mock_page.wait_for_selector = MagicMock()
        # Simulate article page selectors
        mock_page.query_selector_all.return_value = [MagicMock(get_attribute=MagicMock(return_value='/blog/test'))]
        posts = lmarena_scraper.scrape_lmarena_blog(page=mock_page)
        self.assertIsInstance(posts, list)

    def test_scrape_lmarena_blog_empty(self):
        """Test scrape_lmarena_blog returns empty list if no articles found."""
        mock_page = MagicMock()
        mock_page.goto = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[])
        mock_page.wait_for_selector = MagicMock()
        posts = lmarena_scraper.scrape_lmarena_blog(page=mock_page)
        self.assertIsInstance(posts, list)
        self.assertEqual(len(posts), 0)

if __name__ == "__main__":
    unittest.main() 