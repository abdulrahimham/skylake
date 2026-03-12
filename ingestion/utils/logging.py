"""
Logging configuration for SkyLake ingestion layer.

Sets up consistent log formatting across all ingestion modules.
Log level is controlled by the LOG_LEVEL environment variable.
"""

import logging
import os


def setup_logging() -> None:
    """
    Configure logging for the ingestion layer.

    Log level is read from LOG_LEVEL env var.
    Defaults to INFO if not set.
    """
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, level, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
