import unittest
from backend.app.scrapers import rss_scraper
from unittest.mock import MagicMock, patch

class TestRssScraper(unittest.TestCase):
    """Unit tests for the rss_scraper module."""

    @patch('backend.app.scrapers.rss_scraper.feedparser')
    def test_scrape_and_save_rss_feed_success(self, mock_feedparser):
        """Test scrape_and_save_rss_feed saves posts on valid feed."""
        mock_db = MagicMock()
        mock_feed = MagicMock()
        mock_feed.entries = [
            {'title': 'Test', 'link': 'http://example.com', 'summary': 'Summary', 'published': '2023-01-01T00:00:00Z'}
        ]
        mock_feed.bozo = False
        mock_feedparser.parse.return_value = mock_feed
        result = rss_scraper.scrape_and_save_rss_feed(mock_db, 'http://test.com/rss', 'TestSource', 'RSS')
        self.assertIsInstance(result, list)

    @patch('backend.app.scrapers.rss_scraper.feedparser')
    def test_scrape_and_save_rss_feed_invalid_url(self, mock_feedparser):
        """Test scrape_and_save_rss_feed raises on invalid URL."""
        mock_db = MagicMock()
        mock_feedparser.parse.side_effect = Exception('Invalid URL')
        with self.assertRaises(Exception):
            rss_scraper.scrape_and_save_rss_feed(mock_db, 'badurl', 'TestSource', 'RSS')

if __name__ == "__main__":
    unittest.main() 