"""YAML configuration loader with validation for UNIVO-SVIS."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """Raised when configuration validation fails."""


@dataclass
class ModelConfig:
    """Configuration for a single YOLO model."""

    type: str = "ultralytics"
    weights: str = ""
    confidence_threshold: float = 0.35
    class_filter: str = ""


@dataclass
class FusionConfig:
    """Configuration for detection fusion (overlap policy)."""

    overlap_threshold: float = 0.30


@dataclass
class VideoConfig:
    """Configuration for video capture."""

    default_camera_index: int = 0
    target_fps: int = 30
    buffer_size: int = 1


@dataclass
class OutputConfig:
    """Configuration for output directories."""

    captures_dir: str = "output/captures"
    recordings_dir: str = "output/recordings"
    logs_dir: str = "output/logs"


@dataclass
class RoboflowConfig:
    """Configuration for Roboflow vest model access (fallback/resilience)."""

    enabled: bool = False
    workspace: str = ""
    project: str = ""
    version: int = 1
    app_url: str = ""
    universe_url: str = ""
    api_key_env: str = "ROBOFLOW_API_KEY"
    auto_download_weights: bool = False


@dataclass
class AppConfig:
    """Root application configuration."""

    name: str = "UNIVO-SVIS"
    version: str = "0.1.0"
    theme: str = "dark"
    default_mode: str = "home"
    person_model: ModelConfig = field(default_factory=ModelConfig)
    vest_model: ModelConfig = field(default_factory=ModelConfig)
    fusion: FusionConfig = field(default_factory=FusionConfig)
    video: VideoConfig = field(default_factory=VideoConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    roboflow: RoboflowConfig = field(default_factory=RoboflowConfig)


def _validate_threshold(value: float, name: str) -> None:
    """Validate that a threshold is within [0.0, 1.0]."""
    if not 0.0 <= value <= 1.0:
        raise ConfigValidationError(f"Threshold '{name}' must be between 0.0 and 1.0, got {value}")


def _parse_model_config(data: dict, name: str) -> ModelConfig:
    """Parse a model configuration section."""
    if not data:
        raise ConfigValidationError(f"Model config '{name}' is missing or empty")

    config = ModelConfig(
        type=data.get("type", "ultralytics"),
        weights=data.get("weights", ""),
        confidence_threshold=float(data.get("confidence_threshold", 0.35)),
        class_filter=data.get("class_filter", ""),
    )

    if not config.weights:
        raise ConfigValidationError(f"Model '{name}' must specify a 'weights' path")

    _validate_threshold(config.confidence_threshold, f"{name}.confidence_threshold")

    return config


def _check_weights_exist(config: ModelConfig, name: str, project_root: Path) -> None:
    """Warn if model weights file does not exist on disk."""
    weights_path = project_root / config.weights
    if not weights_path.exists():
        logger.warning(
            "Model '%s' weights not found at %s — " "will attempt download or fallback at runtime",
            name,
            weights_path,
        )


def load_config(config_path: str, project_root: Path | None = None) -> AppConfig:
    """Load and validate application configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.
        project_root: Project root directory for resolving relative paths.
            Defaults to the parent of the config file's directory.

    Returns:
        Validated AppConfig instance.

    Raises:
        ConfigValidationError: If required fields are missing or invalid.
        FileNotFoundError: If the config file does not exist.
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    if project_root is None:
        project_root = config_file.parent.parent

    with open(config_file, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    if not raw or not isinstance(raw, dict):
        raise ConfigValidationError("Configuration file is empty or invalid")

    # Parse app section
    app_section = raw.get("app", {})

    # Parse models section
    models_section = raw.get("models", {})
    if not models_section:
        raise ConfigValidationError("'models' section is required in config")

    person_model = _parse_model_config(models_section.get("person", {}), "person")
    vest_model = _parse_model_config(models_section.get("vest", {}), "vest")

    # Check weights existence (warn only, don't crash)
    _check_weights_exist(person_model, "person", project_root)
    _check_weights_exist(vest_model, "vest", project_root)

    # Parse fusion section
    fusion_section = raw.get("fusion", {})
    fusion = FusionConfig(overlap_threshold=float(fusion_section.get("overlap_threshold", 0.30)))
    _validate_threshold(fusion.overlap_threshold, "fusion.overlap_threshold")

    # Parse video section
    video_section = raw.get("video", {})
    video = VideoConfig(
        default_camera_index=int(video_section.get("default_camera_index", 0)),
        target_fps=int(video_section.get("target_fps", 30)),
        buffer_size=int(video_section.get("buffer_size", 1)),
    )

    # Parse output section
    output_section = raw.get("output", {})
    output = OutputConfig(
        captures_dir=output_section.get("captures_dir", "output/captures"),
        recordings_dir=output_section.get("recordings_dir", "output/recordings"),
        logs_dir=output_section.get("logs_dir", "output/logs"),
    )

    # Parse roboflow section
    rf_section = raw.get("roboflow", {})
    roboflow = RoboflowConfig(
        enabled=bool(rf_section.get("enabled", False)),
        workspace=rf_section.get("workspace", ""),
        project=rf_section.get("project", ""),
        version=int(rf_section.get("version", 1)),
        app_url=rf_section.get("app_url", ""),
        universe_url=rf_section.get("universe_url", ""),
        api_key_env=rf_section.get("api_key_env", "ROBOFLOW_API_KEY"),
        auto_download_weights=bool(rf_section.get("auto_download_weights", False)),
    )

    return AppConfig(
        name=app_section.get("name", "UNIVO-SVIS"),
        version=app_section.get("version", "0.1.0"),
        theme=app_section.get("theme", "dark"),
        default_mode=app_section.get("default_mode", "home"),
        person_model=person_model,
        vest_model=vest_model,
        fusion=fusion,
        video=video,
        output=output,
        roboflow=roboflow,
    )
