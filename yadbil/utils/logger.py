import logging
import os
import sys
from typing import Optional

from dotenv import load_dotenv


load_dotenv()

# Configure root logger, otherwise gensim logger doesn't work
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s [%(name)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str = "yadbil", level: Optional[int] = None, log_format: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger with specified settings.

    Args:
        name: Logger name
        level: Logging level
        log_format: Custom log format string

    Returns:
        Configured logger instance
    """
    if level is None:
        level = os.getenv("LOG_LEVEL", logging.INFO)
        if isinstance(level, str):
            level = getattr(logging, level.upper(), logging.INFO)

    if log_format is None:
        log_format = "[%(asctime)s] %(levelname)s [%(name)s] %(message)s"

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(log_format)
    handler.setFormatter(formatter)

    # Add handler to logger if it doesn't already exist
    if not logger.handlers:
        logger.addHandler(handler)

    return logger
