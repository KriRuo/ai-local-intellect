import unittest
from backend.app.utils import pipeline_logger
from unittest.mock import MagicMock, patch

class TestPipelineLogger(unittest.TestCase):
    """Unit tests for the PipelineLogger class."""

    def setUp(self):
        self.mock_db = MagicMock()
        self.logger = pipeline_logger.PipelineLogger(self.mock_db)

    @patch('backend.app.utils.pipeline_logger.RssScrapeRun', autospec=True)
    def test_start_run(self, mock_run):
        """Test start_run creates and adds a run object."""
        self.mock_db.add = MagicMock()
        self.mock_db.commit = MagicMock()
        self.mock_db.refresh = MagicMock()
        mock_run.return_value = MagicMock()
        run = self.logger.start_run('test_source')
        self.mock_db.add.assert_called()
        self.mock_db.commit.assert_called()
        self.mock_db.refresh.assert_called()
        self.assertEqual(run, self.logger.current_run)

    @patch('backend.app.utils.pipeline_logger.PipelineFailure', autospec=True)
    def test_log_article_processed_error(self, mock_failure):
        """Test log_article_processed logs a failure on error status."""
        self.logger.current_run = MagicMock(id=1)
        article = {'url': 'http://example.com'}
        self.mock_db.add = MagicMock()
        self.logger.log_article_processed(article, 'error', 'stage1', 'fail')
        self.assertEqual(self.logger.stats['failed_items'], 1)
        self.mock_db.add.assert_called()
        mock_failure.assert_called()

    def test_log_article_processed_success(self):
        """Test log_article_processed increments success count."""
        self.logger.current_run = MagicMock()
        article = {'url': 'http://example.com'}
        self.logger.log_article_processed(article, 'success', 'stage1')
        self.assertEqual(self.logger.stats['successful_items'], 1)

    def test_log_article_processed_skipped(self):
        """Test log_article_processed increments skipped count."""
        self.logger.current_run = MagicMock()
        article = {'url': 'http://example.com'}
        self.logger.log_article_processed(article, 'skipped', 'stage1')
        self.assertEqual(self.logger.stats['skipped_items'], 1)

if __name__ == '__main__':
    unittest.main() 