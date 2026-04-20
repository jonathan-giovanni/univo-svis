"""View for real-time video and webcam monitoring."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QThread, Slot
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from univo_svis.core.i18n import I18N, Language
from univo_svis.detection.video_worker import VideoWorker
from univo_svis.ui.widgets.control_panel import ControlPanel
from univo_svis.ui.widgets.image_viewer import ImageViewer
from univo_svis.ui.widgets.metrics_panel import MetricsPanel

if TYPE_CHECKING:
    from univo_svis.core.config import AppConfig
    from univo_svis.detection.detector import DualModelDetector

logger = logging.getLogger(__name__)


class LiveMonitorView(QWidget):
    """Dashboard for real-time detection on video streams."""

    def __init__(self, config: AppConfig, detector: DualModelDetector) -> None:
        super().__init__()
        self._config = config
        self._detector = detector

        # Threading infrastructure
        self._worker_thread = QThread()
        self._worker = VideoWorker(self._detector)
        self._worker.moveToThread(self._worker_thread)

        self._setup_ui()
        self._connect_signals()

        # Connect to i18n
        I18N.language_changed.connect(self._on_language_changed)

        self._worker_thread.start()

    def _setup_ui(self) -> None:
        """Layout the live monitoring dashboard."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. Status Strip (FPS, Source, etc)
        self._status_strip = self._create_status_strip()
        layout.addWidget(self._status_strip)

        # 2. Main Center Area (Images + Metrics)
        center_row = QHBoxLayout()
        center_row.setSpacing(10)

        # Dual Image Panels
        self._person_viewer = ImageViewer()
        self._compliance_viewer = ImageViewer()

        center_row.addWidget(self._person_viewer, stretch=2)
        center_row.addWidget(self._compliance_viewer, stretch=2)

        # Metrics Panel (Vertical Sidebar)
        self._metrics_panel = MetricsPanel()
        center_row.addWidget(self._metrics_panel, stretch=1)

        layout.addLayout(center_row, stretch=1)

        # 3. Control Panel (Integrated bottom strip)
        self._controls = self._create_controls()
        layout.addWidget(self._controls)

        self._retranslate_ui()

    def _create_status_strip(self) -> QFrame:
        """Create the top dashboard status indicators."""
        strip = QFrame()
        strip.setFixedHeight(40)
        strip.setStyleSheet(
            "background-color: #1a1a2e; border-radius: 4px; border: 1px solid #37474F;"
        )
        layout = QHBoxLayout(strip)
        layout.setContentsMargins(20, 0, 20, 0)

        self._lbl_fps = QLabel()
        self._lbl_source = QLabel()
        self._lbl_state = QLabel()
        self._lbl_vest_status = QLabel()
        self._lbl_error = QLabel()
        self._lbl_error.setStyleSheet("color: #F44336; font-weight: bold; font-size: 11px;")

        for lbl in [
            self._lbl_fps,
            self._lbl_source,
            self._lbl_state,
            self._lbl_vest_status,
            self._lbl_error,
        ]:
            if lbl != self._lbl_error:
                lbl.setStyleSheet("color: #B0BEC5; font-size: 11px;")
            layout.addWidget(lbl)
            layout.addSpacing(20)

        layout.addStretch()
        return strip

    def _create_controls(self) -> QFrame:
        """Create the bottom action bar."""
        frame = QFrame()
        frame.setStyleSheet(
            "background-color: #263238; border-radius: 8px; border: 1px solid #37474F;"
        )
        main_layout = QHBoxLayout(frame)
        main_layout.setContentsMargins(15, 10, 15, 10)

        # Left side: Thresholds (reusing ControlPanel logic but simplified style)
        self._control_panel = ControlPanel()
        self._control_panel.set_save_enabled(False)  # No save in Live Ph2
        # Use simple trigger logic
        self._control_panel.set_processing_enabled(True)
        # Hide the redundant buttons from ControlPanel, we only want the sliders
        self._control_panel._process_btn.hide()
        self._control_panel._save_btn.hide()
        main_layout.addWidget(self._control_panel, stretch=2)

        # Right side: Source & Playback
        playback_layout = QVBoxLayout()
        playback_layout.setSpacing(10)

        source_row = QHBoxLayout()
        self._source_combo = QComboBox()
        self._source_combo.addItem("Webcam 0", 0)
        self._source_combo.addItem("Webcam 1", 1)
        self._source_combo.addItem("Webcam 2", 2)
        self._source_combo.setFixedWidth(120)

        self._btn_file = QPushButton()
        self._btn_file.clicked.connect(self._on_open_file)

        source_row.addWidget(self._source_combo)
        source_row.addWidget(self._btn_file)
        playback_layout.addLayout(source_row)

        action_row = QHBoxLayout()
        self._btn_start = QPushButton()
        self._btn_pause = QPushButton()
        self._btn_stop = QPushButton()

        self._btn_start.setStyleSheet("background-color: #00BCD4; color: white; font-weight: bold;")
        self._btn_pause.setStyleSheet("background-color: #455A64; color: white;")
        self._btn_stop.setStyleSheet("background-color: #C62828; color: white;")

        self._btn_start.clicked.connect(self._on_start)
        self._btn_pause.clicked.connect(self._on_pause_resume)
        self._btn_stop.clicked.connect(self._on_stop)

        action_row.addWidget(self._btn_start)
        action_row.addWidget(self._btn_pause)
        action_row.addWidget(self._btn_stop)
        playback_layout.addLayout(action_row)

        main_layout.addLayout(playback_layout, stretch=1)

        return frame

    def _connect_signals(self) -> None:
        """Wire worker and UI signals."""
        self._worker.frame_ready.connect(self._on_frame_ready)
        self._worker.metrics_ready.connect(self._metrics_panel.update_metrics)
        self._worker.status_updated.connect(self._on_status_updated)
        self._worker.error_occurred.connect(self._on_error_occurred)

        # Connect sliders from control_panel back to worker
        self._control_panel._person_conf.valueChanged.connect(self._update_worker_thresholds)
        self._control_panel._vest_conf.valueChanged.connect(self._update_worker_thresholds)
        self._control_panel._overlap_thr.valueChanged.connect(self._update_worker_thresholds)

    @Slot(object, object)
    def _on_frame_ready(self, person_frame, compliance_frame) -> None:
        """Convert BGR frames to Pixmap and update viewers."""

        def to_pixmap(frame):
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
            return QPixmap.fromImage(qimg)

        self._person_viewer.setPixmap(to_pixmap(person_frame))
        self._compliance_viewer.setPixmap(to_pixmap(compliance_frame))

    @Slot(dict)
    def _on_status_updated(self, status: dict) -> None:
        """Update the dashboard indicators."""
        self._lbl_fps.setText(f"{I18N.get_text('live_status_fps')}: {status['fps']}")
        self._lbl_source.setText(f"{I18N.get_text('live_status_source')}: {status['source']}")
        self._lbl_state.setText(f"{I18N.get_text('live_status_state')}: {status['state']}")
        self._lbl_vest_status.setText(
            f"{I18N.get_text('live_status_vest')}: {status['vest_status']}"
        )

        # Toggle pause/resume button text
        is_paused = status["state"] == "PAUSED"
        btn_text = I18N.get_text("btn_resume") if is_paused else I18N.get_text("btn_pause")
        self._btn_pause.setText(btn_text)

    @Slot(str)
    def _on_error_occurred(self, message: str) -> None:
        """Display error message in the UI."""
        self._lbl_error.setText(f"!! {message}")
        logger.error("LiveMonitor error signal: %s", message)

    def _update_worker_thresholds(self) -> None:
        """Sync slider values to background worker."""
        p = self._control_panel._person_conf.value() / 100.0
        v = self._control_panel._vest_conf.value() / 100.0
        o = self._control_panel._overlap_thr.value() / 100.0
        self._worker.update_thresholds(p, v, o)

    def _on_start(self) -> None:
        """Start monitoring from selected source."""
        self._lbl_error.clear()
        source = self._source_combo.currentData()
        p = self._control_panel._person_conf.value() / 100.0
        v = self._control_panel._vest_conf.value() / 100.0
        o = self._control_panel._overlap_thr.value() / 100.0
        self._worker.start_monitoring(source, p, v, o)

    def _on_pause_resume(self) -> None:
        """Toggle pause/resume state."""
        # Simple local toggle check based on button text or better, worker state
        # Worker emits status so we'll react to that.
        state = self._lbl_state.text()
        if "PAUSED" in state:
            self._worker.resume_monitoring()
        else:
            self._worker.pause_monitoring()

    def _on_stop(self) -> None:
        """Stop processing."""
        self._worker.stop_monitoring()
        self._person_viewer.clear()
        self._compliance_viewer.clear()
        self._metrics_panel.reset()

    def _on_open_file(self) -> None:
        """Select a video file and start monitoring."""
        self._lbl_error.clear()
        path, _ = QFileDialog.getOpenFileName(
            self, I18N.get_text("open_dialog_title"), "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if path:
            p = self._control_panel._person_conf.value() / 100.0
            v = self._control_panel._vest_conf.value() / 100.0
            o = self._control_panel._overlap_thr.value() / 100.0
            self._worker.start_monitoring(path, p, v, o)

    def shutdown(self) -> None:
        """Gracefully close worker and thread."""
        logger.info("LiveMonitorView shutdown initiated")
        self._worker.stop_monitoring()
        self._worker_thread.quit()
        self._worker_thread.wait()

    def _on_language_changed(self, lang: Language) -> None:
        """Handle language change."""
        self._retranslate_ui()

    def _retranslate_ui(self) -> None:
        """Update translations."""
        self._btn_file.setText(I18N.get_text("btn_open_video"))
        self._btn_start.setText(I18N.get_text("btn_start"))
        # self._btn_pause handled in status update
        self._btn_stop.setText(I18N.get_text("btn_stop"))
