"""Main window shell for UNIVO-SVIS application."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QFont
from PySide6.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QStackedWidget,
    QStatusBar,
    QLabel,
)

from univo_svis.ui.home_view import HomeView

if TYPE_CHECKING:
    from univo_svis.core.config import AppConfig

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Main application window with stacked view navigation."""

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config

        self._setup_window()
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_status_bar()

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
        home_action.triggered.connect(lambda: self._navigate_to(0))
        view_menu.addAction(home_action)

        # Help menu
        help_menu = menu_bar.addMenu("&Help")

        about_action = QAction("&About", self)
        help_menu.addAction(about_action)

    def _setup_central_widget(self) -> None:
        """Create the stacked widget for view navigation."""
        self._stack = QStackedWidget()
        self.setCentralWidget(self._stack)

        # Home view (index 0)
        self._home_view = HomeView(self._config)
        self._stack.addWidget(self._home_view)

        # Navigate to home
        self._stack.setCurrentIndex(0)

    def _setup_status_bar(self) -> None:
        """Create the status bar with model and state indicators."""
        status_bar = self.statusBar()

        # Person model status
        person_label = QLabel(
            f"  Person: {self._config.person_model.weights}  "
        )
        person_label.setStyleSheet("color: #00BCD4; font-size: 11px;")
        status_bar.addWidget(person_label)

        # Separator
        sep = QLabel(" | ")
        sep.setStyleSheet("color: #555; font-size: 11px;")
        status_bar.addWidget(sep)

        # Vest model status
        vest_label = QLabel(
            f"  Vest: {self._config.vest_model.weights}  "
        )
        vest_label.setStyleSheet("color: #FFC107; font-size: 11px;")
        status_bar.addWidget(vest_label)

        # Separator
        sep2 = QLabel(" | ")
        sep2.setStyleSheet("color: #555; font-size: 11px;")
        status_bar.addWidget(sep2)

        # App state
        self._state_label = QLabel("  Ready  ")
        self._state_label.setStyleSheet("color: #4CAF50; font-size: 11px;")
        status_bar.addWidget(self._state_label)

        # Right-side: threshold info
        threshold_label = QLabel(
            f"Confidence: {self._config.person_model.confidence_threshold:.2f} / "
            f"{self._config.vest_model.confidence_threshold:.2f}  |  "
            f"Overlap: {self._config.fusion.overlap_threshold:.2f}  "
        )
        threshold_label.setStyleSheet("color: #999; font-size: 11px;")
        status_bar.addPermanentWidget(threshold_label)

    def _navigate_to(self, index: int) -> None:
        """Navigate to a specific view by index."""
        if 0 <= index < self._stack.count():
            self._stack.setCurrentIndex(index)
            logger.debug("Navigated to view index %d", index)
