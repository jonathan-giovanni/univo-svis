"""Unit tests for YAML configuration loader."""

import tempfile
from pathlib import Path

import pytest
import yaml

from univo_svis.core.config import (
    AppConfig,
    ConfigValidationError,
    load_config,
)


@pytest.fixture
def valid_config_data():
    """Return a valid configuration dictionary."""
    return {
        "app": {
            "name": "UNIVO-SVIS",
            "version": "0.1.0",
            "theme": "dark",
            "default_mode": "home",
        },
        "models": {
            "person": {
                "type": "ultralytics",
                "weights": "models/yolo/yolo11n.pt",
                "confidence_threshold": 0.35,
                "class_filter": "person",
            },
            "vest": {
                "type": "ultralytics",
                "weights": "models/custom/best.pt",
                "confidence_threshold": 0.35,
                "class_filter": "safety_vest",
            },
        },
        "fusion": {"overlap_threshold": 0.30},
        "video": {
            "default_camera_index": 0,
            "target_fps": 30,
            "buffer_size": 1,
        },
        "output": {
            "captures_dir": "output/captures",
            "recordings_dir": "output/recordings",
            "logs_dir": "output/logs",
        },
        "roboflow": {
            "enabled": True,
            "workspace": "jonathans-workspace-zetah",
            "project": "safety-vest-data-yolo",
            "version": 1,
            "app_url": "https://app.roboflow.com/jonathans-workspace-zetah/safety-vest-data-yolo/1",
            "universe_url": "https://universe.roboflow.com/jonathans-workspace-zetah/safety-vest-data-yolo",
            "api_key_env": "ROBOFLOW_API_KEY",
            "auto_download_weights": False,
        },
    }


def _write_config(data: dict, directory: Path) -> Path:
    """Write config data to a YAML file and return its path."""
    config_dir = directory / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "app.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False)
    return config_path


class TestLoadConfig:
    """Tests for the load_config function."""

    def test_loads_valid_config_successfully(self, valid_config_data):
        """Valid config should load without errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            config = load_config(str(config_path), project_root=tmpdir_path)

            assert isinstance(config, AppConfig)
            assert config.name == "UNIVO-SVIS"
            assert config.version == "0.1.0"
            assert config.theme == "dark"

    def test_loads_person_model_config(self, valid_config_data):
        """Person model config should be parsed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            config = load_config(str(config_path), project_root=tmpdir_path)

            assert config.person_model.type == "ultralytics"
            assert config.person_model.weights == "models/yolo/yolo11n.pt"
            assert config.person_model.confidence_threshold == 0.35
            assert config.person_model.class_filter == "person"

    def test_loads_vest_model_config(self, valid_config_data):
        """Vest model config should be parsed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            config = load_config(str(config_path), project_root=tmpdir_path)

            assert config.vest_model.type == "ultralytics"
            assert config.vest_model.weights == "models/custom/best.pt"
            assert config.vest_model.confidence_threshold == 0.35
            assert config.vest_model.class_filter == "safety_vest"

    def test_loads_fusion_config(self, valid_config_data):
        """Fusion config should be parsed correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            config = load_config(str(config_path), project_root=tmpdir_path)

            assert config.fusion.overlap_threshold == 0.30

    def test_loads_roboflow_config(self, valid_config_data):
        """Roboflow config should be parsed with integer version and URLs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            config = load_config(str(config_path), project_root=tmpdir_path)

            assert config.roboflow.enabled is True
            assert config.roboflow.workspace == "jonathans-workspace-zetah"
            assert config.roboflow.project == "safety-vest-data-yolo"
            assert config.roboflow.version == 1
            assert isinstance(config.roboflow.version, int)
            assert "app.roboflow.com" in config.roboflow.app_url
            assert "universe.roboflow.com" in config.roboflow.universe_url

    def test_raises_on_missing_config_file(self):
        """Should raise FileNotFoundError for non-existent config."""
        with pytest.raises(FileNotFoundError):
            load_config("/nonexistent/config.yaml")

    def test_raises_on_missing_models_section(self):
        """Should raise ConfigValidationError when models section is missing."""
        data = {"app": {"name": "test"}}
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(data, tmpdir_path)

            with pytest.raises(ConfigValidationError, match="models"):
                load_config(str(config_path), project_root=tmpdir_path)

    def test_raises_on_missing_model_weights(self):
        """Should raise ConfigValidationError when model weights are not specified."""
        data = {
            "models": {
                "person": {"type": "ultralytics", "confidence_threshold": 0.5},
                "vest": {"type": "ultralytics", "weights": "some.pt"},
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(data, tmpdir_path)

            with pytest.raises(ConfigValidationError, match="weights"):
                load_config(str(config_path), project_root=tmpdir_path)

    def test_raises_on_invalid_confidence_threshold(self, valid_config_data):
        """Should raise ConfigValidationError for out-of-range threshold."""
        valid_config_data["models"]["person"]["confidence_threshold"] = 1.5
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            with pytest.raises(ConfigValidationError, match="threshold"):
                load_config(str(config_path), project_root=tmpdir_path)

    def test_raises_on_negative_threshold(self, valid_config_data):
        """Should raise ConfigValidationError for negative threshold."""
        valid_config_data["fusion"]["overlap_threshold"] = -0.1
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            with pytest.raises(ConfigValidationError, match="threshold"):
                load_config(str(config_path), project_root=tmpdir_path)

    def test_applies_defaults_for_optional_fields(self):
        """Should apply defaults when optional fields are missing."""
        data = {
            "models": {
                "person": {"weights": "person.pt"},
                "vest": {"weights": "vest.pt"},
            }
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(data, tmpdir_path)

            config = load_config(str(config_path), project_root=tmpdir_path)

            # Defaults should be applied
            assert config.name == "UNIVO-SVIS"
            assert config.version == "0.1.0"
            assert config.theme == "dark"
            assert config.person_model.confidence_threshold == 0.35
            assert config.fusion.overlap_threshold == 0.30
            assert config.video.target_fps == 30
            assert config.roboflow.enabled is False

    def test_warns_on_missing_model_files(self, valid_config_data, caplog):
        """Should log warnings when model weight files don't exist on disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_path = _write_config(valid_config_data, tmpdir_path)

            with caplog.at_level("WARNING"):
                config = load_config(str(config_path), project_root=tmpdir_path)

            # Config should still load successfully
            assert config is not None
            # Warnings should have been logged for missing weight files
            assert any("weights not found" in record.message for record in caplog.records)

    def test_raises_on_empty_config_file(self):
        """Should raise ConfigValidationError for an empty YAML file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config" / "app.yaml"
            config_path.parent.mkdir(parents=True)
            config_path.write_text("")

            with pytest.raises(ConfigValidationError, match="empty"):
                load_config(str(config_path), project_root=Path(tmpdir))
