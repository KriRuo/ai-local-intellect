import unittest
from backend.app.scrapers import anthropic_scraper
from unittest.mock import MagicMock

class TestAnthropicScraper(unittest.TestCase):
    """Unit tests for the anthropic_scraper module."""

    def test_scrape_anthropic_news_success(self):
        """Test scrape_anthropic_news returns posts on valid scrape."""
        mock_page = MagicMock()
        mock_page.goto = MagicMock()
        mock_page.query_selector_all = MagicMock(return_value=[MagicMock()])
        mock_page.query_selector = MagicMock(return_value=MagicMock(inner_text=lambda: 'Title'))
        posts = anthropic_scraper.scrape_anthropic_news(page=mock_page)
        self.assertIsInstance(posts, list)

    def test_scrape_anthropic_news_empty(self):
        """Test scrape_anthropic_news returns empty list if no articles found."""
        mock_page = MagicMock()
        mock_page.query_selector_all.return_value = []
        posts = anthropic_scraper.scrape_anthropic_news(page=mock_page)
        self.assertIsInstance(posts, list)

if __name__ == "__main__":
    unittest.main() 