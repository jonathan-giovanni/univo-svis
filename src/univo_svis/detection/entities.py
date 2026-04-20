"""Core domain entities for detection logic."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class DetectionClass(Enum):
    """Supported detection classes."""

    PERSON = "person"
    SAFETY_VEST = "safety_vest"


@dataclass(frozen=True)
class BBox:
    """Bounding box in [x1, y1, x2, y2] format."""

    x1: float
    y1: float
    x2: float
    y2: float

    @property
    def area(self) -> float:
        """Calculate the area of the bounding box."""
        width = max(0.0, self.x2 - self.x1)
        height = max(0.0, self.y2 - self.y1)
        return width * height

    def intersection(self, other: BBox) -> float:
        """Calculate the intersection area with another BBox."""
        ix1 = max(self.x1, other.x1)
        iy1 = max(self.y1, other.y1)
        ix2 = min(self.x2, other.x2)
        iy2 = min(self.y2, other.y2)

        width = max(0.0, ix2 - ix1)
        height = max(0.0, iy2 - iy1)
        return width * height


@dataclass
class Detection:
    """A single object detection result."""

    class_id: str
    class_name: str
    confidence: float
    bbox: BBox


@dataclass
class ComplianceResult:
    """Fused detection result representing a person and their vest status."""

    person: Detection
    has_vest: bool
    vest: Detection | None = None
    overlap_score: float = 0.0
