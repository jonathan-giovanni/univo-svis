"""Widget for selecting and displaying the vest model source."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from univo_svis.detection.detector import DualModelDetector
    from univo_svis.detection.roboflow_resolver import RoboflowResolver

logger = logging.getLogger(__name__)


class ModelSourcePanel(QFrame):
    """Panel to select and display vest model source details."""

    source_changed = Signal(str)

    def __init__(self, detector: DualModelDetector, resolver: RoboflowResolver) -> None:
        super().__init__()
        self._detector = detector
        self._resolver = resolver

        self._setup_ui()
        self._update_details()

    def _setup_ui(self) -> None:
        self.setStyleSheet(
            "ModelSourcePanel { "
            "background-color: #1E272C; "
            "border: 1px solid #37474F; "
            "border-radius: 6px; "
            "}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(20)

        # 1. Selector
        selector_layout = QVBoxLayout()
        selector_label = QLabel("Vest Model Source:")
        selector_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        selector_label.setStyleSheet("color: #B0BEC5;")
        
        self._combo = QComboBox()
        self._combo.setFont(QFont("Segoe UI", 10))
        self._combo.addItem("Local Model", "local")
        self._combo.addItem("Roboflow Serverless", "api")
        self._combo.setMinimumWidth(180)
        
        # Set initial combo state based on detector
        idx = self._combo.findData(self._detector.vest_mode)
        if idx >= 0:
            self._combo.setCurrentIndex(idx)
            
        self._combo.currentIndexChanged.connect(self._on_combo_changed)
        
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self._combo)
        
        layout.addLayout(selector_layout)

        # Vertical separator
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFrameShadow(QFrame.Shadow.Sunken)
        sep.setStyleSheet("color: #37474F;")
        layout.addWidget(sep)

        # 2. Details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        
        self._status_title = QLabel("Source Details")
        self._status_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._status_title.setStyleSheet("color: #B0BEC5;")
        
        self._details_label = QLabel()
        self._details_label.setFont(QFont("Segoe UI", 9))
        self._details_label.setStyleSheet("color: #78909C;")
        self._details_label.setWordWrap(True)
        
        details_layout.addWidget(self._status_title)
        details_layout.addWidget(self._details_label)
        layout.addLayout(details_layout, stretch=1)

    def _on_combo_changed(self) -> None:
        mode = self._combo.currentData()
        self._detector.set_vest_mode(mode)
        self._update_details()
        self.source_changed.emit(mode)

    def _update_details(self) -> None:
        """Update the details text based on the active mode."""
        mode = self._detector.vest_mode
        
        text = ""
        if mode in ("local", "local_error"):
            text += "Mode: Local Model\n"
            text += f"Path: {self._resolver.get_local_path() or self._resolver._local_weights}\n"
            
            if mode == "local":
                text += "<span style='color: #4CAF50; font-weight: bold;'>Status: READY</span>"
            else:
                text += "<span style='color: #F44336; font-weight: bold;'>Status: ERROR - Weights not found</span>"
        
        elif mode in ("api", "api_error"):
            text += "Mode: Roboflow Serverless\n"
            text += "API URL: https://serverless.roboflow.com\n"
            text += f"Model ID: {self._resolver._project}/{self._resolver._version}\n"
            url = f"https://app.roboflow.com/{self._resolver._workspace}/{self._resolver._project}/{self._resolver._version}"
            text += f"Project URL: {url}\n"
            
            if mode == "api":
                 text += "<span style='color: #FFC107; font-weight: bold;'>Status: READY (API Key Configured)</span>"
            elif not self._resolver._api_key:
                text += "<span style='color: #F44336; font-weight: bold;'>Status: ERROR - API Key missing (set ROBOFLOW_API_KEY)</span>"
            else:
                text += "<span style='color: #F44336; font-weight: bold;'>Status: ERROR - Failed to connect or initialize model</span>"
                    
        self._details_label.setText(text)
