"""View for static image analysis with dual-panel display."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from univo_svis.core.i18n import I18N, Language
from univo_svis.detection.detector import DualModelDetector
from univo_svis.detection.image_analysis import run_static_analysis
from univo_svis.ui.widgets.control_panel import ControlPanel
from univo_svis.ui.widgets.image_viewer import ImageViewer
from univo_svis.ui.widgets.metrics_panel import MetricsPanel

if TYPE_CHECKING:
    from univo_svis.core.config import AppConfig

logger = logging.getLogger(__name__)


class ImageAnalysisView(QWidget):
    """Main view for processing static images with responsive rendering and i18n."""

    def __init__(self, config: AppConfig, detector: DualModelDetector) -> None:
        super().__init__()
        self._config = config
        self._detector = detector
        self._current_image: np.ndarray | None = None
        self._current_path: str | None = None

        self._setup_ui()

        # Connect to i18n
        I18N.language_changed.connect(self._on_language_changed)

    def _setup_ui(self) -> None:
        """Create the layout with dual panels, metrics, and controls."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. Header Area: Status and File info
        header_layout = QHBoxLayout()

        self._file_label = QLabel()
        self._file_label.setStyleSheet("color: #B0BEC5; font-style: italic;")

        self._model_status = QLabel()
        self._update_model_status_label()

        self._open_btn = QPushButton()
        self._open_btn.setMinimumWidth(150)
        self._open_btn.clicked.connect(self._on_open_image)

        header_layout.addWidget(self._file_label)
        header_layout.addStretch()
        header_layout.addWidget(self._model_status)
        header_layout.addWidget(self._open_btn)

        main_layout.addLayout(header_layout)

        # 2. Results Metrics Panel
        self._metrics = MetricsPanel()
        main_layout.addWidget(self._metrics)

        # 3. Dual Panel Area
        panels_container = QHBoxLayout()
        panels_container.setSpacing(15)

        # Left Panel: Person Detection
        self._person_viewer = ImageViewer()
        self._person_panel_layout, self._person_title = self._create_panel(self._person_viewer)
        panels_container.addLayout(self._person_panel_layout, stretch=1)

        # Right Panel: Fused Compliance
        self._compliance_viewer = ImageViewer()
        self._compliance_panel_layout, self._compliance_title = self._create_panel(
            self._compliance_viewer
        )
        panels_container.addLayout(self._compliance_panel_layout, stretch=1)

        main_layout.addLayout(panels_container, stretch=1)

        # 4. Bottom Controls
        self._controls = ControlPanel()
        self._controls.process_requested.connect(self._on_process_requested)
        self._controls.save_requested.connect(self._on_save_requested)
        main_layout.addWidget(self._controls)

        self._retranslate_ui()

    def _create_panel(self, viewer: ImageViewer) -> tuple[QVBoxLayout, QLabel]:
        """Helper to create a panel with a title and image viewer."""
        layout = QVBoxLayout()
        layout.setSpacing(5)

        title_lbl = QLabel()
        title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_lbl.setStyleSheet(
            "color: #78909C; font-weight: bold; "
            "background: #263238; padding: 5px; border-radius: 4px;"
        )

        layout.addWidget(title_lbl)
        layout.addWidget(viewer, stretch=1)

        return layout, title_lbl

    def _update_model_status_label(self) -> None:
        """Update the model status sub-label."""
        mode_text = I18N.get_text("header_vest_mode")
        mode_val = self._detector.vest_mode.upper()
        self._model_status.setText(f"{mode_text}: {mode_val}")

        mode_colors = {"local": "#4CAF50", "api": "#FFC107", "none": "#F44336"}
        self._model_status.setStyleSheet(
            f"color: {mode_colors.get(self._detector.vest_mode, '#999')}; font-weight: bold;"
        )

    @Slot()
    def _on_open_image(self) -> None:
        """Open a file dialog to select an image."""
        path, _ = QFileDialog.getOpenFileName(
            self, I18N.get_text("open_dialog_title"), "", "Images (*.png *.jpg *.jpeg *.bmp)"
        )
        if not path:
            return

        image = cv2.imread(path)
        if image is None:
            logger.error("Failed to load image at %s", path)
            return

        self._current_image = image
        self._current_path = path
        self._file_label.setText(f"File: {Path(path).name}")

        # Display raw image in both viewers initially
        pixmap = self._cv_to_pixmap(image)
        self._person_viewer.setPixmap(pixmap)
        self._compliance_viewer.setPixmap(pixmap)

        # Enable processing
        self._controls.set_processing_enabled(True)
        self._controls.set_save_enabled(False)
        self._metrics.reset()

        logger.info("Image loaded: %s", path)

    @Slot(float, float, float)
    def _on_process_requested(
        self, person_conf: float, vest_conf: float, overlap_thr: float
    ) -> None:
        """Execute the analysis pipeline."""
        if self._current_image is None:
            return

        # Update confidence thresholds in config
        self._config.person_model.confidence_threshold = person_conf
        self._config.vest_model.confidence_threshold = vest_conf

        # Run analysis
        result = run_static_analysis(self._current_image, self._detector, overlap_thr)

        # 1. Update Metrics
        self._metrics.update_metrics(
            result.total_persons, result.compliant_count, result.non_compliant_count
        )

        # 2. Annotation
        # Left Panel: Person only
        person_img = self._annotator.annotate_persons(self._current_image, result.persons)

        # Right Panel: Fused Compliance
        compliance_img = self._annotator.annotate_compliance(self._current_image, result.compliance)

        # 3. Display
        self._person_viewer.setPixmap(self._cv_to_pixmap(person_img))
        self._compliance_viewer.setPixmap(self._cv_to_pixmap(compliance_img))

        # Store for saving
        self._latest_result_img = compliance_img
        self._controls.set_save_enabled(True)

    @Slot()
    def _on_save_requested(self) -> None:
        """Save the processed compliance image."""
        if not hasattr(self, "_latest_result_img"):
            return

        default_name = f"result_{Path(self._current_path).stem}.jpg"
        save_path, _ = QFileDialog.getSaveFileName(
            self, I18N.get_text("save_dialog_title"), default_name, "JPEG (*.jpg);;PNG (*.png)"
        )

        if save_path:
            cv2.imwrite(save_path, self._latest_result_img)
            logger.info("Result saved to %s", save_path)

    def _cv_to_pixmap(self, cv_img: np.ndarray) -> QPixmap:
        """Convert BGR OpenCV image to QPixmap."""
        rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        q_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        return QPixmap.fromImage(q_img)

    def _on_language_changed(self, lang: Language) -> None:
        """Handle language changed signal."""
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update visible text labels."""
        if not self._current_path:
            self._file_label.setText(I18N.get_text("status_no_image"))
            self._person_viewer.setText(I18N.get_text("panel_no_image"))
            self._compliance_viewer.setText(I18N.get_text("panel_no_image"))

        self._update_model_status_label()
        self._open_btn.setText(I18N.get_text("btn_open_image"))

        self._person_title.setText(I18N.get_text("panel_person"))
        self._compliance_title.setText(I18N.get_text("panel_compliance"))
