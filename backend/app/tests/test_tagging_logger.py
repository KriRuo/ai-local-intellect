import unittest
from backend.app.utils import tagging_logger

class TestTaggingLogger(unittest.TestCase):
    """Unit tests for the TaggingLogger class.
    These tests verify that the logger correctly tracks and reports the status of tagging operations.
    """

    def setUp(self):
        # Create a new logger instance for each test to ensure isolation
        self.logger = tagging_logger.TaggingLogger()

    def test_log_processed_success(self):
        """
        Test that logging a 'success' status increments the 'successful' count in stats.
        Ensures that successful tagging operations are tracked.
        """
        self.logger.log_processed('success')
        self.assertEqual(self.logger.stats['successful'], 1)

    def test_log_processed_error(self):
        """
        Test that logging an 'error' status increments the 'failed' count in stats
        and that the error message is recorded in the logger's errors list.
        Ensures that failures are tracked and error details are preserved.
        """
        self.logger.log_processed('error', error_message='fail')
        self.assertEqual(self.logger.stats['failed'], 1)
        self.assertIn('fail', self.logger.errors)

    def test_log_processed_skipped(self):
        """
        Test that logging a 'skipped' status increments the 'skipped' count in stats.
        Ensures that skipped tagging operations are tracked.
        """
        self.logger.log_processed('skipped')
        self.assertEqual(self.logger.stats['skipped'], 1)

    def test_print_summary(self):
        """
        Test that print_summary runs without error after logging a success.
        This ensures the summary method is robust and does not raise exceptions.
        """
        self.logger.log_processed('success')
        self.logger.print_summary()  # Should not raise

if __name__ == '__main__':
    unittest.main() 