"""Clause banks for the narration pipeline.

Each bank is a nested dictionary: dict[str, dict[str, list[str]]]
Outer key = sub-type, inner key = intensity band, value = clause list.

Intensity bands:
    calm      (0.0 - 0.3)  -- lowercase, flowing, minimal drama
    building  (0.3 - 0.6)  -- tension starts, ellipses, some color
    hype      (0.6 - 0.85) -- exclamation points, shorter clauses
    screaming (0.85 - 1.0) -- ALL CAPS, announcer losing it
"""

from __future__ import annotations

from typing import Dict, List

# Type alias for clause banks
ClauseBank = Dict[str, Dict[str, List[str]]]

# Intensity band boundaries
INTENSITY_CALM = (0.0, 0.3)
INTENSITY_BUILDING = (0.3, 0.6)
INTENSITY_HYPE = (0.6, 0.85)
INTENSITY_SCREAMING = (0.85, 1.0)


def intensity_band(intensity: float) -> str:
    """Map a 0.0-1.0 intensity float to a band name."""
    if intensity < 0.3:
        return "calm"
    if intensity < 0.6:
        return "building"
    if intensity < 0.85:
        return "hype"
    return "screaming"
