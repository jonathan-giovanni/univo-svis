#!/usr/bin/env python3
"""Smoke test — verifies core imports, config loading, and logging without launching GUI."""

import sys
from pathlib import Path

# Add src to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))


def test_imports():
    """Verify all core modules can be imported."""
    print("[SMOKE] Testing imports...")
    import univo_svis
    from univo_svis.core.config import load_config, AppConfig
    from univo_svis.core.logger import setup_logging
    from univo_svis.core.bootstrap import bootstrap
    print(f"  ✓ univo_svis v{univo_svis.__version__}")
    print("  ✓ All core imports successful")


def test_config_loading():
    """Verify config loads and validates correctly."""
    print("[SMOKE] Testing config loading...")
    from univo_svis.core.config import load_config

    config_path = PROJECT_ROOT / "config" / "app.yaml"
    config = load_config(str(config_path), project_root=PROJECT_ROOT)

    assert config.name == "UNIVO-SVIS", f"Expected UNIVO-SVIS, got {config.name}"
    assert config.person_model.weights == "models/yolo/yolo11n.pt"
    assert config.vest_model.weights == "models/custom/best.pt"
    assert config.fusion.overlap_threshold == 0.30
    assert config.roboflow.workspace == "jonathans-workspace-zetah"
    assert config.roboflow.project == "safety-vest-data-yolo"
    assert config.roboflow.version == 1
    print("  ✓ Config loaded and validated successfully")
    print(f"  ✓ App: {config.name} v{config.version}")
    print(f"  ✓ Person model: {config.person_model.weights}")
    print(f"  ✓ Vest model: {config.vest_model.weights}")
    print(f"  ✓ Overlap threshold: {config.fusion.overlap_threshold}")


def test_logging():
    """Verify logging setup works."""
    print("[SMOKE] Testing logging...")
    from univo_svis.core.logger import setup_logging
    import logging
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        setup_logging(log_dir=tmpdir)
        logger = logging.getLogger("smoke_test")
        logger.info("Smoke test log message")
        print("  ✓ Logging initialized and writing")


def test_bootstrap():
    """Verify full bootstrap works."""
    print("[SMOKE] Testing bootstrap...")
    from univo_svis.core.bootstrap import bootstrap

    config = bootstrap()
    assert config.name == "UNIVO-SVIS"
    print("  ✓ Bootstrap completed successfully")


def main():
    """Run all smoke tests."""
    print("=" * 50)
    print("  UNIVO-SVIS Smoke Test")
    print("=" * 50)

    tests = [test_imports, test_config_loading, test_logging, test_bootstrap]
    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1

    print()
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
