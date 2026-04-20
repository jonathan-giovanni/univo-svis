"""Application bootstrap — loads config, initializes logging, prepares runtime."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from univo_svis.infrastructure.config.yaml_config_loader import AppConfig, load_config
from univo_svis.infrastructure.logging.logger_factory import setup_logging

logger = logging.getLogger(__name__)

# Project root is two levels up from this file (src/univo_svis/bootstrap.py → project root)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config" / "app.yaml"


def bootstrap(config_path: str | None = None) -> AppConfig:
    """Bootstrap the application: load config, setup logging, validate environment.

    Args:
        config_path: Optional path to config file. Defaults to config/app.yaml.

    Returns:
        Validated AppConfig instance.
    """
    path = config_path or str(DEFAULT_CONFIG_PATH)

    # Load configuration first (before logging, so we know log dir)
    try:
        config = load_config(path, project_root=PROJECT_ROOT)
    except Exception as e:
        # Fallback: print to stderr since logging isn't set up yet
        print(f"[FATAL] Failed to load configuration: {e}", file=sys.stderr)
        raise

    # Setup logging using config output paths
    log_dir = str(PROJECT_ROOT / config.output.logs_dir)
    setup_logging(log_dir=log_dir)

    # Ensure output directories exist
    for dir_path in [
        config.output.captures_dir,
        config.output.recordings_dir,
        config.output.logs_dir,
    ]:
        (PROJECT_ROOT / dir_path).mkdir(parents=True, exist_ok=True)

    # Log startup banner
    logger.info("=" * 60)
    logger.info("  %s v%s", config.name, config.version)
    logger.info("  Safety Vest Inspection Suite")
    logger.info("  University of Oviedo")
    logger.info("=" * 60)
    logger.info("Person model  : %s (%s)", config.person_model.weights, config.person_model.type)
    logger.info("Vest model    : %s (%s)", config.vest_model.weights, config.vest_model.type)
    logger.info("Confidence    : person=%.2f, vest=%.2f",
                config.person_model.confidence_threshold,
                config.vest_model.confidence_threshold)
    logger.info("Overlap thr.  : %.2f", config.fusion.overlap_threshold)
    logger.info("Theme         : %s", config.theme)
    logger.info("Project root  : %s", PROJECT_ROOT)

    return config
