"""
Thread-safe logging setup for the server.

Configures a rotating log file (`webserver.log`) with UTC timestamps and
queue-based logging to safely handle messages from multiple threads.
"""

import logging
import time
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import Queue

LOG_FILE = "webserver.log"
_listener = None  # pylint: disable=invalid-name


class UTCFormatter(logging.Formatter):
    """
    Custom logging formatter that uses UTC (GMT) for timestamps instead of local time.

    This ensures logs are timezone-consistent across systems, which is especially
    useful in distributed environments.
    """

    converter = time.gmtime


def get_logger():
    """
    Initializes and configures the server logger with:
      - INFO-level logging
      - A queue-based logging system for thread safety
      - RotatingFileHandler to limit log file size and keep history
      - UTC timestamps

    Returns:
        logging.Logger: The configured logger instance.

    Notes:
        - Only the QueueHandler is attached to the logger to avoid duplicate logging.
        - The actual file writing is handled asynchronously by the QueueListener.
        - The global `listener` is used so the queue can be shut down gracefully.
    """

    global _listener  # pylint: disable=global-statement

    logger = logging.getLogger(LOG_FILE)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if logger.hasHandlers():
        logger.handlers.clear()

    formatter = UTCFormatter(
        fmt="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)

    log_queue = Queue()
    queue_handler = QueueHandler(log_queue)
    logger.addHandler(queue_handler)

    _listener = QueueListener(log_queue, file_handler)
    _listener.start()

    return logger
