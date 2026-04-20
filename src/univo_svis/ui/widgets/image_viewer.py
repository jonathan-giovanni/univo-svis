"""Responsive image viewer widget that preserves aspect ratio."""

from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel, QSizePolicy

logger = logging.getLogger(__name__)


class ImageViewer(QLabel):
    """
    A QLabel that scales its pixmap to fit its size while preserving aspect ratio.
    Ensures the image is always centered and never stretched beyond its original size
    if requested (default: fits container).
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._original_pixmap: QPixmap | None = None
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(1, 1)  # Allow shrinking
        self.setStyleSheet("background-color: #000000;")  # Black backgrounds for padding

    def setPixmap(self, pixmap: QPixmap) -> None:
        """Store the original pixmap and trigger an initial scale."""
        self._original_pixmap = pixmap
        self._update_display()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Handle widget resize by rescaling the pixmap."""
        super().resizeEvent(event)
        if self._original_pixmap:
            self._update_display()

    def _update_display(self) -> None:
        """Scale and set the pixmap based on current widget size."""
        if not self._original_pixmap or self._original_pixmap.isNull():
            return

        # Target size is the current widget size
        target_size = self.size()

        # Scale pixmap preserving aspect ratio
        # We use SmoothTransformation for better quality
        scaled = self._original_pixmap.scaled(
            target_size,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        # Call the base class setPixmap with the scaled version
        # Note: We must call super().setPixmap to avoid recursion if we overrode it
        super().setPixmap(scaled)

    def clear(self) -> None:
        """Clear the images."""
        self._original_pixmap = None
        super().clear()
        self.setText("")
