"""Application-wide logging setup."""

import logging
import sys


def setup_logger() -> logging.Logger:
    """Configures and returns a standard logger for the application.

    Logs are written to standard output.
    """
    app_logger = logging.getLogger("wa_catalog_bot")

    if not app_logger.handlers:
        app_logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        app_logger.addHandler(console_handler)

    return app_logger


logger = setup_logger()
