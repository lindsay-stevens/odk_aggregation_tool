import logging
import collections


class CapturingHandler(logging.Handler):
    """
    A logging handler capturing all (raw and formatted) logging output.

    Largely the same as doing "from unittest.case import _CapturingHandler",
    but copied here because it is a simple class, and the original has an
    underscore prefix so it might change unexpectedly.

    Usage:
    Here's how to attach it to a logger, get the logs, and then detach it.

    my_logger = logging.getLogger(name="logger_name")
    capture_handler = _CapturingHandler(logger=my_logger)
    log_messages = capture_handler.watcher.output
    log_records = capture_handler.watcher.records
    my_logger.removeHandler(hdlr=capture_handler)
    """

    def __init__(self, logger, name=None):
        logging.Handler.__init__(self)
        _LoggingWatcher = collections.namedtuple(
            "_LoggingWatcher", ["records", "output"])
        self.watcher = _LoggingWatcher([], [])
        if name is not None:
            self.name = name
        existing_capture = [x for x in logger.handlers if x.name == name]
        if len(existing_capture) == 0:
            logger.addHandler(self)
        else:
            logger.info("Skipped adding handler '{0}', a logging handler "
                        "with the same name is already attached.".format(name))

    def flush(self):
        pass

    def emit(self, record):
        self.watcher.records.append(record)
        msg = self.format(record)
        self.watcher.output.append(msg)
