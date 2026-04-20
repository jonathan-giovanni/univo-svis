from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from univo_svis.core.i18n import I18N, Language

if TYPE_CHECKING:
    from univo_svis.core.config import AppConfig

logger = logging.getLogger(__name__)


class HomeView(QWidget):
    """Home screen with project branding and mode navigation cards."""

    # Signals for navigation
    analyze_image_requested = Signal()
    live_monitor_requested = Signal()

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self._config = config
        self._setup_ui()

        # Connect to i18n
        I18N.language_changed.connect(self._on_language_changed)

    def _setup_ui(self) -> None:
        """Build the home screen layout."""
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(60, 60, 60, 60)

        # 1. Branding
        self._title_lbl = QLabel(self._config.name)
        self._title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._title_lbl.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        self._title_lbl.setStyleSheet("color: #00BCD4; letter-spacing: 4px;")
        layout.addWidget(self._title_lbl)

        self._subtitle_lbl = QLabel()
        self._subtitle_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._subtitle_lbl.setFont(QFont("Segoe UI", 18))
        self._subtitle_lbl.setStyleSheet("color: #B0BEC5; letter-spacing: 2px;")
        layout.addWidget(self._subtitle_lbl)

        self._univ_lbl = QLabel()
        self._univ_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._univ_lbl.setFont(QFont("Segoe UI", 14))
        self._univ_lbl.setStyleSheet("color: #78909C; font-style: italic;")
        layout.addWidget(self._univ_lbl)

        layout.addSpacing(40)

        # 2. Action Cards
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(30)

        self._btn_image, self._card_image_title, self._card_image_desc = self._create_action_card(
            actions_layout,
            "",  # Title set in retranslate
            "",  # Desc set in retranslate
            self.analyze_image_requested,
        )

        self._btn_live, self._card_live_title, self._card_live_desc = self._create_action_card(
            actions_layout,
            "",  # Title set in retranslate
            "",  # Desc set in retranslate
            self.live_monitor_requested,
        )

        layout.addLayout(actions_layout)

        layout.addSpacing(40)

        # 3. Config Summary Footer
        self._footer_header = QLabel()
        self._add_config_footer(layout)

        self._retranslate_ui()

    def _create_action_card(
        self, layout: QHBoxLayout, title: str, desc: str, signal: Signal
    ) -> tuple[QPushButton, QLabel, QLabel]:
        """Create a large, styled action card."""
        container = QFrame()
        container.setMinimumSize(320, 220)
        container.setStyleSheet(
            "QFrame { background-color: #263238; border-radius: 12px; border: 2px solid #37474F; }"
            "QFrame:hover { border: 2px solid #00BCD4; background-color: #37474F; }"
        )

        vbox = QVBoxLayout(container)
        vbox.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vbox.setSpacing(10)

        title_lbl = QLabel(title)
        title_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        title_lbl.setStyleSheet("color: #00BCD4; border: none; background: transparent;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        desc_lbl = QLabel(desc)
        desc_lbl.setFont(QFont("Segoe UI", 10))
        desc_lbl.setStyleSheet("color: #B0BEC5; border: none; background: transparent;")
        desc_lbl.setWordWrap(True)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        vbox.addWidget(title_lbl)
        vbox.addWidget(desc_lbl)

        # Button overlay to capture clicks
        btn = QPushButton(container)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setStyleSheet("background: transparent; border: none;")
        btn.setFixedSize(320, 220)
        btn.clicked.connect(signal.emit)

        layout.addWidget(container)
        return btn, title_lbl, desc_lbl

    def _add_config_footer(self, layout: QVBoxLayout) -> None:
        """Add a footer showing active configuration summary."""
        footer_frame = QFrame()
        footer_frame.setStyleSheet(
            "QFrame { "
            "background-color: #1a1a2e; "
            "border-radius: 8px; "
            "padding: 12px; "
            "border: 1px solid #37474F; "
            "}"
        )
        footer_layout = QVBoxLayout(footer_frame)

        self._footer_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._footer_header.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        self._footer_header.setStyleSheet("color: #78909C;")
        footer_layout.addWidget(self._footer_header)

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

    def _on_language_changed(self, lang: Language) -> None:
        """Handle language changed signal."""
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update visibile text labels."""
        self._subtitle_lbl.setText(I18N.get_text("app_subtitle"))
        self._univ_lbl.setText(I18N.get_text("university"))

        self._card_image_title.setText(I18N.get_text("nav_image_analysis"))
        self._card_image_desc.setText(I18N.get_text("home_analyze_desc"))

        self._card_live_title.setText(I18N.get_text("nav_live_monitor"))
        self._card_live_desc.setText(I18N.get_text("home_monitor_desc"))

        self._footer_header.setText(I18N.get_text("home_footer_config"))
