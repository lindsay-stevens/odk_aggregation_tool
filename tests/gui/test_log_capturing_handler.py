import unittest
import logging
from odk_aggregation_tool.gui.log_capturing_handler import CapturingHandler


class TestCapturingHandler(unittest.TestCase):
    """Tests for the CapturingHandler class."""

    def test_capture_handler_output(self):
        """Should return list of log messages."""
        test_logger = logging.getLogger("my_test_logger")
        test_logger.setLevel("INFO")
        capture = CapturingHandler(logger=test_logger)
        messages = ["first message", "this is a second message"]
        test_logger.warning(messages[0])
        test_logger.info(messages[1])
        test_logger.removeHandler(hdlr=capture)
        self.assertEqual(capture.watcher.output, messages)

    def test_capturing_handler_avoids_duplicate_name(self):
        """Should skip adding a duplicate handler name and log a message."""
        test_logger = logging.getLogger("my_test_logger")
        test_logger.setLevel("INFO")
        capture = CapturingHandler(logger=test_logger, name="my_logger")
        CapturingHandler(logger=test_logger, name="my_logger")
        message = "Skipped adding handler 'my_logger'"
        self.assertIn(message, capture.watcher.output[0])
        self.assertEqual(test_logger.handlers, [capture])
