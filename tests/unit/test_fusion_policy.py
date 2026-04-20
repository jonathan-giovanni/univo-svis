"""Unit tests for the vest overlap policy (IOA_vest)."""

from univo_svis.detection.entities import BBox, Detection
from univo_svis.detection.fusion import calculate_compliance


def test_calculate_compliance_exact_overlap():
    """Test with a vest perfectly inside a person box."""
    # Vest: (100, 100) to (200, 200), Area = 10000
    # Person: (50, 50) to (250, 250)
    person = Detection("0", "person", 0.9, BBox(50, 50, 250, 250))
    vest = Detection("1", "safety_vest", 0.8, BBox(100, 100, 200, 200))

    results = calculate_compliance([person], [vest], overlap_threshold=0.30)

    assert len(results) == 1
    assert results[0].has_vest is True
    # IOA_vest = 10000 / 10000 = 1.0
    assert results[0].overlap_score == 1.0


def test_calculate_compliance_partial_overlap_above_threshold():
    """Test with 50% of the vest inside the person box."""
    # Vest: (100, 100) to (200, 200), Area = 10000
    # Person: (50, 50) to (150, 250)
    # Intersection: (100, 100) to (150, 200), Area = 50 * 100 = 5000
    # IOA_vest = 5000 / 10000 = 0.5
    person = Detection("0", "person", 0.9, BBox(50, 50, 150, 250))
    vest = Detection("1", "safety_vest", 0.8, BBox(100, 100, 200, 200))

    results = calculate_compliance([person], [vest], overlap_threshold=0.30)

    assert results[0].has_vest is True
    assert results[0].overlap_score == 0.5


def test_calculate_compliance_partial_overlap_below_threshold():
    """Test with 20% of the vest inside the person box (threshold is 0.30)."""
    # Vest: (100, 100) to (200, 200), Area = 10000
    # Person: (0, 0) to (120, 250)
    # Intersection: (100, 100) to (120, 200), Area = 20 * 100 = 2000
    # IOA_vest = 2000 / 10000 = 0.2
    person = Detection("0", "person", 0.9, BBox(0, 0, 120, 250))
    vest = Detection("1", "safety_vest", 0.8, BBox(100, 100, 200, 200))

    results = calculate_compliance([person], [vest], overlap_threshold=0.30)

    assert results[0].has_vest is False
    assert results[0].overlap_score == 0.2


def test_calculate_compliance_no_overlap():
    """Test with person and vest completely separated."""
    person = Detection("0", "person", 0.9, BBox(0, 0, 50, 50))
    vest = Detection("1", "safety_vest", 0.8, BBox(100, 100, 150, 150))

    results = calculate_compliance([person], [vest])

    assert results[0].has_vest is False
    assert results[0].overlap_score == 0.0


def test_calculate_compliance_multiple_vests():
    """Ensure person picks the vest with the HIGHEST overlap."""
    person = Detection("0", "person", 0.9, BBox(50, 50, 250, 250))
    vest1 = Detection("1", "safety_vest", 0.8, BBox(100, 100, 150, 150))  # Area 2500, Score 1.0
    vest2 = Detection("2", "safety_vest", 0.8, BBox(150, 150, 200, 200))  # Area 2500, Score 1.0
    # In this case both have 1.0, will pick the first one found that is > max_score
    # Let's make one better:
    vest1 = Detection("1", "safety_vest", 0.8, BBox(100, 100, 180, 180))  # Area 6400, Score 1.0
    vest2 = Detection(
        "2", "safety_vest", 0.8, BBox(200, 200, 300, 300)
    )  # Area 10000, 2500 overlap, Score 0.25

    results = calculate_compliance([person], [vest1, vest2], overlap_threshold=0.30)

    assert results[0].has_vest is True
    assert results[0].vest == vest1
    assert results[0].overlap_score == 1.0
