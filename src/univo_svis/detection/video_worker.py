"""Background worker for video processing using QObject thread pattern."""

from __future__ import annotations

import logging
import time
import traceback
from typing import TYPE_CHECKING

import cv2
import numpy as np
from PySide6.QtCore import QObject, Signal, Slot

from univo_svis.detection.annotator import Annotator
from univo_svis.detection.fusion import calculate_compliance

if TYPE_CHECKING:
    import numpy as np

    from univo_svis.detection.detector import DualModelDetector

logger = logging.getLogger(__name__)


class VideoWorker(QObject):
    """
    Worker for processing video frames in a background thread.
    Use QObject.moveToThread(thread) pattern.
    """

    # Signals for UI communication
    frame_ready = Signal(object, object)  # (person_annotated, compliance_annotated)
    metrics_ready = Signal(int, int, int)  # (total, with_vest, without_vest)
    status_updated = Signal(dict)  # {fps, source, state, vest_status}
    error_occurred = Signal(str)

    def __init__(self, detector: DualModelDetector) -> None:
        super().__init__()
        self._detector = detector
        self._annotator = Annotator()

        # State control
        self._running = False
        self._paused = False
        self._source_path: str | int | None = None
        self._capture: cv2.VideoCapture | None = None

        # Performance monitoring
        self._fps = 0.0
        self._frame_count = 0
        self._start_time = 0.0

        # Thresholds
        self._person_conf = 0.35
        self._vest_conf = 0.35
        self._overlap_thr = 0.30

    @Slot(object, float, float, float)
    def start_monitoring(
        self, source: str | int, p_conf: float, v_conf: float, o_thr: float
    ) -> None:
        """Initialize capture and start the processing loop."""
        if self._running:
            self.stop_monitoring()

        logger.info("Starting video monitoring: source=%s", source)
        self._source_path = source
        self._person_conf = p_conf
        self._vest_conf = v_conf
        self._overlap_thr = o_thr

        self._capture = cv2.VideoCapture(source)
        if not self._capture.isOpened():
            self.error_occurred.emit(f"Failed to open source: {source}")
            return

        self._running = True
        self._paused = False
        self._start_time = time.time()
        self._frame_count = 0
        self._run_loop()

    @Slot()
    def pause_monitoring(self) -> None:
        """Pause the processing loop."""
        self._paused = True
        self._update_status()

    @Slot()
    def resume_monitoring(self) -> None:
        """Resume the processing loop."""
        self._paused = False
        self._update_status()

    @Slot()
    def stop_monitoring(self) -> None:
        """Stop the loop and release resources."""
        self._running = False
        if self._capture:
            self._capture.release()
            self._capture = None
        logger.info("Video monitoring stopped")
        self._update_status()

    @Slot(float, float, float)
    def update_thresholds(self, p_conf: float, v_conf: float, o_thr: float) -> None:
        """Update detection thresholds on the fly."""
        self._person_conf = p_conf
        self._vest_conf = v_conf
        self._overlap_thr = o_thr

    def _run_loop(self) -> None:
        """Main processing loop with latest-frame strategy and robust error handling."""
        try:
            while self._running:
                if self._paused:
                    time.sleep(0.1)
                    continue

                ret, frame = self._capture.read()
                if not ret or frame is None:
                    # End of file or connection lost
                    if isinstance(self._source_path, str):
                        logger.info("End of video file reached: %s", self._source_path)
                        self.stop_monitoring()
                    else:
                        self.error_occurred.emit("Lost connection to camera")
                        self.stop_monitoring()
                    break

                if frame.size == 0:
                    continue

                # 1. Detection & Fusion
                self._process_frame(frame)
                self._update_performance()
                self._update_status()

                # Manual yield to prevent thread saturation
                time.sleep(0.001)
        except Exception:
            err_msg = traceback.format_exc()
            logger.error("Critical error in VideoWorker loop:\n%s", err_msg)
            self.error_occurred.emit(f"Worker Error: {err_msg.splitlines()[-1]}")
            self.stop_monitoring()

    def _process_frame(self, frame: np.ndarray) -> None:
        """Run the detection pipeline on a single frame."""
        try:
            # 1. Inference
            # Use 'conf' keyword as defined in the repaired detector
            persons = self._detector.detect_persons(frame, conf=self._person_conf)
            vest_conf = self._vest_conf if self._detector.has_vest_model else None
            vests = self._detector.detect_vests(frame, conf=vest_conf)
            compliance = calculate_compliance(persons, vests, self._overlap_thr)

            # 2. Annotation
            # Left Panel: Person only
            person_img = frame.copy()
            self._annotator.annotate_persons(person_img, persons)

            # Right Panel: Fused Compliance
            compliance_img = frame.copy()
            self._annotator.annotate_compliance(compliance_img, compliance)

            # 3. Signals
            self.frame_ready.emit(person_img, compliance_img)

            compliant_count = sum(1 for c in compliance if c.has_vest)
            self.metrics_ready.emit(len(persons), compliant_count, len(persons) - compliant_count)
        except Exception:
            err_msg = traceback.format_exc()
            logger.error("Error processing frame:\n%s", err_msg)
            # We don't stop the loop for a single frame error, but we log it.
            # If it's a persistent API error, the loop's try-except will eventually catch it.
            raise

    def _update_performance(self) -> None:
        """Track FPS."""
        self._frame_count += 1
        elapsed = time.time() - self._start_time
        if elapsed >= 1.0:
            self._fps = self._frame_count / elapsed
            self._frame_count = 0
            self._start_time = time.time()

    def _update_status(self) -> None:
        """Emit current runtime status."""
        vest_status = "READY" if self._detector.has_vest_model else "FALLBACK/OFF"
        if not self._running:
            state = "STOPPED"
        elif self._paused:
            state = "PAUSED"
        else:
            state = "RUNNING"

        status = {
            "fps": f"{self._fps:.1f}",
            "source": str(self._source_path),
            "state": state,
            "vest_status": vest_status,
        }
        self.status_updated.emit(status)
