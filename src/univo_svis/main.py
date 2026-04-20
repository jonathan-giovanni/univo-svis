"""UNIVO-SVIS application entry point."""

from __future__ import annotations

import logging
import sys

logger = logging.getLogger(__name__)


def main() -> None:
    """Launch the UNIVO-SVIS desktop application."""
    # Import PySide6 early to catch missing dependency
    try:
        from PySide6.QtWidgets import QApplication
    except ImportError:
        print(
            "[FATAL] PySide6 is not installed. "
            "Run: pip install -r requirements.txt",
            file=sys.stderr,
        )
        sys.exit(1)

    # Bootstrap: load config, setup logging
    from univo_svis.core.bootstrap import bootstrap

    try:
        config = bootstrap()
    except Exception as e:
        print(f"[FATAL] Bootstrap failed: {e}", file=sys.stderr)
        sys.exit(1)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName(config.name)
    app.setApplicationVersion(config.version)

    # Apply dark theme
    try:
        import qdarktheme

        app.setStyleSheet(qdarktheme.load_stylesheet())
        logger.info("Dark theme applied via qdarktheme")
    except ImportError:
        logger.warning("qdarktheme not available — using default theme")
    except Exception as e:
        logger.warning("Failed to apply dark theme: %s", e)

    # Create and show main window
    from univo_svis.ui.main_window import MainWindow

    window = MainWindow(config)
    window.show()

    logger.info("Application started — entering event loop")

    # Run event loop
    exit_code = app.exec()

    logger.info("Application exiting with code %d", exit_code)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
