"""Logging configuration for the application."""

import logging
import sys
from backend.app.core.config import settings


def setup_logging() -> logging.Logger:
    """Configures and returns the application logger."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Configure root logger format
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        force=True,
    )

    logger = logging.getLogger("yojana_sahayak")
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
