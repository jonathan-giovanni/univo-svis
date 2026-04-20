from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from univo_svis.core.i18n import I18N, Language

logger = logging.getLogger(__name__)


class MetricsPanel(QFrame):
    """Stateless widget for displaying person and compliance totals."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

        # Connect to i18n
        I18N.language_changed.connect(self._on_language_changed)

    def _setup_ui(self) -> None:
        """Build the metrics display layout."""
        self.setStyleSheet(
            "MetricsPanel { "
            "background-color: #1a1a2e; border-radius: 8px; border: 1px solid #37474F; "
            "}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(40)

        # 1. Total Persons
        self._total_label, self._total_title = self._create_metric_item(layout, "0", "#00BCD4")

        # 2. Persons with Vest
        self._with_vest_label, self._with_vest_title = self._create_metric_item(
            layout, "0", "#4CAF50"
        )

        # 3. Persons without Vest
        self._without_vest_label, self._without_vest_title = self._create_metric_item(
            layout, "0", "#F44336"
        )

        self._retranslate_ui()

    def _create_metric_item(
        self, layout: QHBoxLayout, initial_value: str, color: str
    ) -> tuple[QLabel, QLabel]:
        """Helper to create a single vertical metric display."""
        item_layout = QVBoxLayout()
        item_layout.setSpacing(5)

        title_lbl = QLabel()
        title_lbl.setFont(QFont("Segoe UI", 10))
        title_lbl.setStyleSheet("color: #90A4AE;")
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        value_lbl = QLabel(initial_value)
        value_lbl.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        value_lbl.setStyleSheet(f"color: {color};")
        value_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        item_layout.addWidget(title_lbl)
        item_layout.addWidget(value_lbl)
        layout.addLayout(item_layout)

        return value_lbl, title_lbl

    def update_metrics(self, total: int, with_vest: int, without_vest: int) -> None:
        """Update the values displayed in the panel."""
        self._total_label.setText(str(total))
        self._with_vest_label.setText(str(with_vest))
        self._without_vest_label.setText(str(without_vest))
        logger.debug("Metrics updated: %d/%d/%d", total, with_vest, without_vest)

    def reset(self) -> None:
        """Reset metrics to zero."""
        self.update_metrics(0, 0, 0)

    def _on_language_changed(self, lang: Language) -> None:
        """Handle language changed signal."""
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update visible metric titles."""
        self._total_title.setText(I18N.get_text("metric_total"))
        self._with_vest_title.setText(I18N.get_text("metric_with_vest"))
        self._without_vest_title.setText(I18N.get_text("metric_without_vest"))
