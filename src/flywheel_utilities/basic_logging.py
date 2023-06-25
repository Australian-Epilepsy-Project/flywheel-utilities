"""
Setup basic logging with the log level determined from the Flywheel manifest
variable 'gear-log-level'.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

# Enable explicit type hints with mypy
if TYPE_CHECKING:
    from flywheel_geartoolkit_context import GearToolkitContext


def setup_basic_logging(
    context: GearToolkitContext,
    log_format: str = "[%(asctime)s %(levelname)s] %(message)s",
    log_date: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    """
    Basic formatting for logger

    Parameters
    ----------
    context:
        Flywheel context object
    log_format:
        desired logging print format
    log_date:
        desired logging date format
    """

    # Setup basic logging
    if "gear-log-level" in context.config:
        if context.config["gear-log-level"] == "DEBUG":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level, format=log_format, datefmt=log_date)

    logger = logging.getLogger()
    logger.info("Logger initialised")
