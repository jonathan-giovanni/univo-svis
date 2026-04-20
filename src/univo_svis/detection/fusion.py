"""Fusion logic for vest compliance analysis."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from univo_svis.detection.entities import ComplianceResult

if TYPE_CHECKING:
    from univo_svis.detection.entities import Detection

logger = logging.getLogger(__name__)


def calculate_compliance(
    persons: list[Detection],
    vests: list[Detection],
    overlap_threshold: float = 0.30,
) -> list[ComplianceResult]:
    """Fuse person and vest detections based on IOA (Intersection over Area of Vest).

    Logic:
    For each person, find the vest with the highest IOA.
    If IOA > threshold, mark as COMPLIANT.

    Formula:
    overlap = intersection_area(person, vest) / Area(vest)

    Args:
        persons: List of detected person objects.
        vests: List of detected vest objects.
        overlap_threshold: Minimum IOA to consider a vest as belonging to a person.

    Returns:
        List of ComplianceResult objects.
    """
    results = []

    for person in persons:
        best_vest: Detection | None = None
        max_score = 0.0

        for vest in vests:
            # Formula: intersection / vest_area
            vest_area = vest.bbox.area
            if vest_area <= 0:
                continue

            intersection = person.bbox.intersection(vest.bbox)
            score = intersection / vest_area

            if score > max_score:
                max_score = score
                best_vest = vest

        has_vest = max_score >= overlap_threshold

        results.append(
            ComplianceResult(
                person=person,
                has_vest=has_vest,
                vest=best_vest if has_vest else None,
                overlap_score=max_score,
            )
        )

    logger.debug(
        "Fusion complete: %d persons, %d vests -> %d results",
        len(persons),
        len(vests),
        len(results),
    )
    return results
