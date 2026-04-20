"""Main window shell for UNIVO-SVIS application."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from univo_svis.core.i18n import I18N, Language
from univo_svis.detection.detector import DualModelDetector
from univo_svis.detection.roboflow_resolver import RoboflowResolver
from univo_svis.ui.home_view import HomeView
from univo_svis.ui.image_analysis_view import ImageAnalysisView
from univo_svis.ui.live_monitor_view import LiveMonitorView

if TYPE_CHECKING:
    from PySide6.QtGui import QCloseEvent

    from univo_svis.core.config import AppConfig

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with stacked view navigation."""

    VIEW_HOME = 0
    VIEW_IMAGE_ANALYSIS = 1
    VIEW_LIVE_MONITOR = 2

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config

        # Initialize shared resolver and detector
        resolver = RoboflowResolver(
            local_weights=config.vest_model.weights,
            workspace=config.roboflow.workspace,
            project=config.roboflow.project,
            version=config.roboflow.version,
            project_root=Path("."),
        )
        self._detector = DualModelDetector(self._config, resolver)

        self._setup_window()
        self._setup_status_bar()
        self._setup_ui()

        # Initial text update once all widgets are created
        self._retranslate_ui()

        # Start at home view
        self._navigate_to(self.VIEW_HOME)

        # Connect to i18n service
        I18N.language_changed.connect(self._on_language_changed)

        logger.info("Main window initialized")

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle(f"{self._config.name} — Safety Vest Inspection Suite")
        self.setMinimumSize(1200, 800)

    def _setup_menu_bar(self) -> None:
        """Create the application menu bar."""
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        open_image_action = QAction("Open &Image...", self)
        open_image_action.setShortcut("O")
        file_menu.addAction(open_image_action)

        open_video_action = QAction("Open &Video...", self)
        open_video_action.setShortcut("V")
        file_menu.addAction(open_video_action)

        open_webcam_action = QAction("Open &Webcam", self)
        open_webcam_action.setShortcut("W")
        file_menu.addAction(open_webcam_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menu_bar.addMenu("&View")

        home_action = QAction("&Home", self)
        home_action.triggered.connect(self._navigate_to_home)
        view_menu.addAction(home_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        about_action = QAction("&About", self)
        help_menu.addAction(about_action)

    def _setup_ui(self) -> None:
        """Build the main UI layout with header and stacked content."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Top Header Bar
        header = QFrame()
        header.setFixedHeight(60)
        header.setStyleSheet(
            "QFrame { background-color: #1a1a2e; border-bottom: 2px solid #00BCD4; }"
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        title_lbl = QLabel("UNIVO-SVIS")
        title_lbl.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #00BCD4; background: transparent;")

        self._lang_selector = QComboBox()
        self._lang_selector.addItem("English", Language.EN)
        self._lang_selector.addItem("Español", Language.ES)
        self._lang_selector.setFixedWidth(120)
        self._lang_selector.currentIndexChanged.connect(self._change_language)

        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self._lang_selector)

        main_layout.addWidget(header)

        # 2. Stacked Content Area
        self._stack = QStackedWidget()
        main_layout.addWidget(self._stack)

        # Home View
        self._home_view = HomeView(self._config)
        self._home_view.analyze_image_requested.connect(
            lambda: self._navigate_to(self.VIEW_IMAGE_ANALYSIS)
        )
        self._home_view.live_monitor_requested.connect(
            lambda: self._navigate_to(self.VIEW_LIVE_MONITOR)
        )
        self._stack.addWidget(self._home_view)

        # Image Analysis View (index 1)
        self._image_analysis_view = ImageAnalysisView(self._config, self._detector)
        self._stack.addWidget(self._image_analysis_view)

        # Live Monitor View (index 2)
        self._live_monitor_view = LiveMonitorView(self._config, self._detector)
        self._stack.addWidget(self._live_monitor_view)

    def _setup_status_bar(self) -> None:
        """Create the status bar with model and state indicators."""
        status_bar = self.statusBar()

        # Left side: Current mode/view indicator
        self._mode_label = QLabel()
        self._mode_label.setStyleSheet("font-weight: bold; color: #00BCD4;")
        status_bar.addWidget(self._mode_label)

        # Separator
        sep = QLabel(" | ")
        sep.setStyleSheet("color: #555;")
        status_bar.addWidget(sep)

        # App state
        self._state_label = QLabel()
        self._state_label.setStyleSheet("color: #4CAF50;")
        status_bar.addWidget(self._state_label)

    def _change_language(self, index: int) -> None:
        """Signal language change to the i18n service."""
        lang = self._lang_selector.itemData(index)
        I18N.set_language(lang)

    def _on_language_changed(self, lang: Language) -> None:
        """Handle language changed signal."""
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update visible text in the MainWindow according to current language."""
        self.setWindowTitle(f"{I18N.get_text('app_name')} — {I18N.get_text('app_subtitle')}")
        self._update_mode_label()
        self._state_label.setText(f"  {I18N.get_text('header_ready')}  ")

    def _navigate_to_home(self) -> None:
        """Navigate back to the home screen."""
        self._navigate_to(0)

    def _navigate_to(self, index: int) -> None:
        """Navigate to a specific view by index."""
        if 0 <= index < self._stack.count():
            # If leaving live monitor, stop it
            if self._stack.currentIndex() == self.VIEW_LIVE_MONITOR:
                self._live_monitor_view._on_stop()

            self._stack.setCurrentIndex(index)
            self._update_mode_label()
            logger.debug("Navigated to view index %d", index)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Ensure clean shutdown of background threads."""
        logger.info("Main window closing - shutting down services")
        self._live_monitor_view.shutdown()
        event.accept()

    def _update_mode_label(self) -> None:
        """Update the mode label in the status bar."""
        index = self._stack.currentIndex()
        modes = {
            self.VIEW_HOME: I18N.get_text("nav_home"),
            self.VIEW_IMAGE_ANALYSIS: I18N.get_text("nav_image_analysis"),
            self.VIEW_LIVE_MONITOR: I18N.get_text("nav_live_monitor"),
        }
        self._mode_label.setText(f"  {modes.get(index, 'UNKNOWN')}  ")
