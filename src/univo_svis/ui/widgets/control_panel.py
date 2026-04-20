from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from univo_svis.core.i18n import I18N, Language


class ControlPanel(QFrame):
    """Widget containing sliders for thresholds and the primary action button."""

    # Signal emitted when 'Process' is clicked.
    # Sends (person_conf, vest_conf, overlap_thr)
    process_requested = Signal(float, float, float)

    # Signal emitted when 'Save' is clicked
    save_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

        # Connect to i18n
        I18N.language_changed.connect(self._on_language_changed)

    def _setup_ui(self) -> None:
        """Build the control layout."""
        self.setStyleSheet(
            "ControlPanel { "
            "background-color: #1a1a2e; border-radius: 8px; border: 1px solid #37474F; "
            "}"
            "QPushButton#process_btn { "
            "background-color: #00BCD4; color: white; font-weight: bold; "
            "padding: 10px; border-radius: 5px; "
            "}"
            "QPushButton#process_btn:disabled { "
            "background-color: #37474F; color: #78909C; "
            "}"
            "QPushButton#save_btn { "
            "background-color: #455A64; color: white; "
            "padding: 10px; border-radius: 5px; "
            "}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(30)

        # 1. Thresholds Column
        thr_layout = QVBoxLayout()

        self._person_conf, self._person_lbl = self._add_slider(thr_layout, 0.35)
        self._vest_conf, self._vest_lbl = self._add_slider(thr_layout, 0.35)
        self._overlap_thr, self._overlap_lbl = self._add_slider(thr_layout, 0.30)

        layout.addLayout(thr_layout, stretch=2)

        # 2. Actions Column
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        self._process_btn = QPushButton()
        self._process_btn.setObjectName("process_btn")
        self._process_btn.setMinimumHeight(50)
        self._process_btn.setEnabled(False)
        self._process_btn.clicked.connect(self._on_process_clicked)

        self._save_btn = QPushButton()
        self._save_btn.setObjectName("save_btn")
        self._save_btn.setEnabled(False)
        self._save_btn.clicked.connect(self.save_requested.emit)

        btn_layout.addWidget(self._process_btn)
        btn_layout.addWidget(self._save_btn)

        layout.addLayout(btn_layout, stretch=1)

        self._retranslate_ui()

    def _add_slider(self, layout: QVBoxLayout, default: float) -> tuple[QSlider, QLabel]:
        """Add a slider with a title label."""
        row_layout = QHBoxLayout()

        lbl = QLabel()
        lbl.setStyleSheet("color: #B0BEC5;")
        lbl.setMinimumWidth(150)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(default * 100))

        val_lbl = QLabel(f"{default:.2f}")
        val_lbl.setStyleSheet("color: #00BCD4; font-weight: bold;")
        val_lbl.setMinimumWidth(40)

        slider.valueChanged.connect(lambda v: val_lbl.setText(f"{v/100:.2f}"))

        row_layout.addWidget(lbl)
        row_layout.addWidget(slider)
        row_layout.addWidget(val_lbl)
        layout.addLayout(row_layout)

        return slider, lbl

    def set_processing_enabled(self, enabled: bool) -> None:
        """Enable or disable the Process button (e.g. if image loaded)."""
        self._process_btn.setEnabled(enabled)

    def set_save_enabled(self, enabled: bool) -> None:
        """Enable or disable the Save button."""
        self._save_btn.setEnabled(enabled)

    def _on_process_clicked(self) -> None:
        """Emit the process signal with current slider values."""
        self.process_requested.emit(
            self._person_conf.value() / 100.0,
            self._vest_conf.value() / 100.0,
            self._overlap_thr.value() / 100.0,
        )

    def _on_language_changed(self, lang: Language) -> None:
        """Handle language changed signal."""
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update visible text in the control panel."""
        self._person_lbl.setText(I18N.get_text("control_person_conf"))
        self._vest_lbl.setText(I18N.get_text("control_vest_conf"))
        self._overlap_lbl.setText(I18N.get_text("control_overlap"))

        self._process_btn.setText(I18N.get_text("btn_process"))
        self._save_btn.setText(I18N.get_text("btn_save"))
