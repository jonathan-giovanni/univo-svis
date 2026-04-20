"""Visualization logic for drawing detections on images."""

from __future__ import annotations

import cv2
import numpy as np

from univo_svis.detection.entities import ComplianceResult, Detection


class Annotator:
    """Draws detections and compliance results on images using OpenCV."""

    COLORS = {
        "person": (212, 188, 0),  # Cyan-ish (BGR)
        "safety_vest": (7, 193, 255),  # Amber-ish (BGR)
        "compliant": (76, 175, 80),  # Material Green (BGR)
        "non_compliant": (36, 36, 244),  # Material Red (BGR)
    }

    @classmethod
    def draw_persons(cls, image: np.ndarray, persons: list[Detection]) -> np.ndarray:
        """Draw only person detections on the image (for Left Panel)."""
        canvas = image.copy()
        color = cls.COLORS["person"]

        for p in persons:
            cls._draw_box(canvas, p.bbox, color, f"Person {p.confidence:.2f}")

        return canvas

    @classmethod
    def draw_compliance(cls, image: np.ndarray, results: list[ComplianceResult]) -> np.ndarray:
        """Draw compliance results on the image (for Right Panel)."""
        canvas = image.copy()

        for res in results:
            # Determine color based on compliance
            color = cls.COLORS["compliant"] if res.has_vest else cls.COLORS["non_compliant"]
            label = "VEST OK" if res.has_vest else "NO VEST"

            # 1. Draw Person Box with compliance color
            cls._draw_box(
                canvas, res.person.bbox, color, f"{label} ({res.overlap_score:.2f})", thickness=3
            )

            # 2. Draw Vest Box (if present) to show what was detected
            if res.vest:
                cls._draw_box(
                    canvas,
                    res.vest.bbox,
                    cls.COLORS["safety_vest"],
                    "",
                    thickness=1,
                    style=cv2.LINE_AA,
                )

        return canvas

    @staticmethod
    def _draw_box(
        image: np.ndarray,
        bbox,
        color: tuple[int, int, int],
        label: str,
        thickness: int = 2,
        style: int = cv2.LINE_8,
    ) -> None:
        """Helper to draw a single bounding box and label."""
        x1, y1, x2, y2 = map(int, [bbox.x1, bbox.y1, bbox.x2, bbox.y2])

        # Draw box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, thickness, style)

        if label:
            # Draw label background
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            font_thickness = 1
            text_size = cv2.getTextSize(label, font, font_scale, font_thickness)[0]

            # Ensure label stays within bounds
            label_y = max(y1, text_size[1] + 5)
            cv2.rectangle(
                image, (x1, label_y - text_size[1] - 5), (x1 + text_size[0], label_y), color, -1
            )

            # Draw label text
            cv2.putText(
                image,
                label,
                (x1, label_y - 5),
                font,
                font_scale,
                (255, 255, 255),
                font_thickness,
                cv2.LINE_AA,
            )
