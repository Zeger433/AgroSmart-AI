"""Structured logging setup using loguru."""

from __future__ import annotations

import sys
from pathlib import Path

from loguru import logger

from src.utils.paths import project_root


def configure_logging(level: str = "INFO", log_file: str | None = None) -> None:
    """Configure loguru sinks for console (and optional file).

    Args:
        level: Minimum log level (DEBUG, INFO, WARNING, ERROR).
        log_file: Relative path under project root for file logging; None skips file.
    """
    logger.remove()
    logger.add(sys.stderr, level=level, enqueue=True, backtrace=False, diagnose=False)
    if log_file:
        path = project_root() / log_file
        path.parent.mkdir(parents=True, exist_ok=True)
        logger.add(path, level=level, rotation="10 MB", retention="7 days", enqueue=True)
