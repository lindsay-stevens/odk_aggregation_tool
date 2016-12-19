import unittest
import logging
from odk_aggregation_tool.gui.log_capturing_handler import CapturingHandler

test_logger = logging.getLogger(__name__)
test_logger.addHandler(logging.NullHandler())
test_logger.setLevel("INFO")
test_logger.propagate = False


class TestCapturingHandler(unittest.TestCase):
    """Tests for the CapturingHandler class."""

    def test_capture_handler_output(self):
        """Should return list of log messages."""
        capture = CapturingHandler(logger=test_logger, name=__name__)
        messages = ["first message", "this is a second message"]
        test_logger.warning(messages[0])
        test_logger.info(messages[1])
        test_logger.removeHandler(hdlr=capture)
        self.assertEqual(capture.watcher.output, messages)

    def test_capturing_handler_avoids_duplicate_name(self):
        """Should skip adding a duplicate handler name and log a message."""
        capture = CapturingHandler(logger=test_logger, name=__name__)
        CapturingHandler(logger=test_logger, name=__name__)
        message = "Skipped adding handler"
        self.assertIn(message, capture.watcher.output[0])
        self.assertIn(capture, test_logger.handlers)
        self.assertEqual(2, len(test_logger.handlers))
