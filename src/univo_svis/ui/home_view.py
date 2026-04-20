"""Home view — landing screen for UNIVO-SVIS."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from univo_svis.core.config import AppConfig

logger = logging.getLogger(__name__)


class HomeView(QWidget):
    """Home screen with project branding and mode navigation placeholders.

    Phase 0: Shows project title and branding only.
    Phase 1: Will add action cards for image/video analysis modes.
    """

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Build the home screen layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 60, 60, 60)

        # Title
        title = QLabel(self._config.name)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        title.setStyleSheet("color: #00BCD4; letter-spacing: 4px;")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("Safety Vest Inspection Suite")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setFont(QFont("Segoe UI", 18))
        subtitle.setStyleSheet("color: #B0BEC5; letter-spacing: 2px;")
        layout.addWidget(subtitle)

        # University
        university = QLabel("University of Oviedo")
        university.setAlignment(Qt.AlignmentFlag.AlignCenter)
        university.setFont(QFont("Segoe UI", 14))
        university.setStyleSheet("color: #78909C; font-style: italic;")
        layout.addWidget(university)

        # Spacer
        layout.addSpacing(30)

        # Divider line
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("color: #37474F;")
        layout.addWidget(divider)

        layout.addSpacing(20)

        # Phase 0 placeholder — action cards come in Phase 1
        placeholder = QLabel("Analysis modes will be available in the next phase")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setFont(QFont("Segoe UI", 12))
        placeholder.setStyleSheet("color: #546E7A;")
        layout.addWidget(placeholder)

        layout.addSpacing(40)

        # Config summary footer
        self._add_config_footer(layout)

    def _add_config_footer(self, layout: QVBoxLayout) -> None:
        """Add a footer showing active configuration summary."""
        footer_frame = QFrame()
        footer_frame.setStyleSheet(
            "QFrame { background-color: #1a1a2e; border-radius: 8px; padding: 12px; }"
        )
        footer_layout = QVBoxLayout(footer_frame)

        header = QLabel("Active Configuration")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        header.setStyleSheet("color: #78909C;")
        footer_layout.addWidget(header)

        info_row = QHBoxLayout()
        info_row.setSpacing(30)

        items = [
            ("Person Model", self._config.person_model.weights, "#00BCD4"),
            ("Vest Model", self._config.vest_model.weights, "#FFC107"),
            (
                "Confidence",
                f"{self._config.person_model.confidence_threshold:.2f} / "
                f"{self._config.vest_model.confidence_threshold:.2f}",
                "#4CAF50",
            ),
            ("Overlap", f"{self._config.fusion.overlap_threshold:.2f}", "#FF9800"),
            ("Theme", self._config.theme, "#9E9E9E"),
        ]

        for label_text, value_text, color in items:
            item_layout = QVBoxLayout()
            item_layout.setSpacing(2)

            label = QLabel(label_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Segoe UI", 9))
            label.setStyleSheet("color: #546E7A;")
            item_layout.addWidget(label)

            value = QLabel(str(value_text))
            value.setAlignment(Qt.AlignmentFlag.AlignCenter)
            value.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
            value.setStyleSheet(f"color: {color};")
            item_layout.addWidget(value)

            info_row.addLayout(item_layout)

        footer_layout.addLayout(info_row)
        layout.addWidget(footer_frame)
