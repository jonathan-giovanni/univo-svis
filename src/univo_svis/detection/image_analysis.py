"""Minimal image analysis pipeline for static images."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from univo_svis.detection.fusion import calculate_compliance

if TYPE_CHECKING:
    import numpy as np

    from univo_svis.detection.detector import DualModelDetector
    from univo_svis.detection.entities import ComplianceResult, Detection


logger = logging.getLogger(__name__)


@dataclass
class StaticAnalysisResult:
    """Container for the results of a single static image analysis."""

    persons: list[Detection]
    vests: list[Detection]
    compliance: list[ComplianceResult]
    total_persons: int
    compliant_count: int
    non_compliant_count: int


def run_static_analysis(
    image: np.ndarray, detector: DualModelDetector, overlap_threshold: float = 0.30
) -> StaticAnalysisResult:
    """Run the complete detection and fusion pipeline on a single image.

    Args:
        image: BGR image array (OpenCV format).
        detector: The dual-model detector coordinator.
        overlap_threshold: Threshold for IOA_vest fusion.

    Returns:
        StaticAnalysisResult object containing all detections and counts.
    """
    logger.info("Starting static image analysis...")

    # 1. Detect Persons
    persons = detector.detect_persons(image)

    # 2. Detect Vests
    vests = detector.detect_vests(image)

    # 3. Fuse Detections
    compliance = calculate_compliance(persons, vests, overlap_threshold)

    # 4. Calculate Metrics
    compliant_count = sum(1 for c in compliance if c.has_vest)
    non_compliant_count = len(persons) - compliant_count

    result = StaticAnalysisResult(
        persons=persons,
        vests=vests,
        compliance=compliance,
        total_persons=len(persons),
        compliant_count=compliant_count,
        non_compliant_count=non_compliant_count,
    )

    logger.info(
        "Analysis complete. Found %d persons: %d with vest, %d without.",
        result.total_persons,
        result.compliant_count,
        result.non_compliant_count,
    )

    return result
