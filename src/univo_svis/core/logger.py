"""Logging configuration factory for UNIVO-SVIS."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_dir: str = "output/logs", level: str = "INFO") -> None:
    """Configure application-wide logging with console and file handlers.

    Args:
        log_dir: Directory for log files. Created if missing.
        level: Logging level string (DEBUG, INFO, WARNING, ERROR, CRITICAL).
    """
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_path / f"univo_svis_{timestamp}.log"

    log_level = getattr(logging, level.upper(), logging.INFO)

    # Root logger configuration
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Clear existing handlers to avoid duplicates on re-init
    root_logger.handlers.clear()

    # Log format
    fmt = logging.Formatter(
        "[%(asctime)s] %(levelname)-8s %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(fmt)
    root_logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler(str(log_file), encoding="utf-8")
    file_handler.setLevel(log_level)
    file_handler.setFormatter(fmt)
    root_logger.addHandler(file_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("ultralytics").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    logging.getLogger(__name__).info(
        "Logging initialized — level=%s, file=%s", level, log_file
    )
