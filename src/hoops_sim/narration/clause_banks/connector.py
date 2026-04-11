"""Clause bank for connectors between clauses.

Connectors are chosen based on role transition and intensity trend.
"""

# (from_role, to_role, intensity_trend) -> connector options
CONNECTOR_MAP: dict[tuple[str, str, str], list[str]] = {
    # establish -> establish
    ("establish", "establish", "flat"): [", ", ", "],
    ("establish", "establish", "rising"): [", ", "... "],
    # establish -> build
    ("establish", "build", "flat"): [", ", "... "],
    ("establish", "build", "rising"): ["... ", ", "],
    # build -> build
    ("build", "build", "flat"): [", ", "... "],
    ("build", "build", "rising"): ["... ", ", ", "-- "],
    # build -> pivot
    ("build", "pivot", "flat"): ["... ", "! "],
    ("build", "pivot", "rising"): ["! ", "... "],
    # pivot -> climax
    ("pivot", "climax", "flat"): ["! ", ", "],
    ("pivot", "climax", "rising"): ["! ", ", "],
    # climax -> aftermath
    ("climax", "aftermath", "any"): ["! ", ". "],
    ("climax", "aftermath", "flat"): ["! ", ". "],
    ("climax", "aftermath", "falling"): ["! ", ". "],
    # aftermath -> aftermath
    ("aftermath", "aftermath", "any"): [" ", "! "],
    ("aftermath", "aftermath", "flat"): [" ", ". "],
    ("aftermath", "aftermath", "falling"): [" ", ". "],
    # establish -> pivot (skip build)
    ("establish", "pivot", "rising"): ["... ", "! "],
    ("establish", "pivot", "flat"): ["... ", ", "],
    # establish -> climax (very short possession)
    ("establish", "climax", "rising"): ["... ", "! "],
    ("establish", "climax", "flat"): ["... ", "! "],
    # build -> climax (skip pivot)
    ("build", "climax", "rising"): ["! ", "... "],
    ("build", "climax", "flat"): ["... ", "! "],
    # pivot -> aftermath (skip climax -- rare)
    ("pivot", "aftermath", "any"): ["! ", ". "],
    ("pivot", "aftermath", "flat"): ["! ", ". "],
    ("pivot", "aftermath", "falling"): ["! ", ". "],
    # pivot -> pivot (multiple pivots)
    ("pivot", "pivot", "rising"): ["! ", ", "],
    ("pivot", "pivot", "flat"): ["... ", "! "],
    # aside transitions
    ("aside", "build", "flat"): [". ", " "],
    ("aside", "climax", "rising"): [". ", " "],
    ("build", "aside", "flat"): [". ", " "],
}

# Fallback connectors when no specific mapping exists
FALLBACK_CONNECTORS = {
    "flat": [", ", " "],
    "rising": ["... ", "! "],
    "falling": [". ", " "],
    "any": [", ", " "],
}


def get_connectors(
    from_role: str, to_role: str, intensity_trend: str,
) -> list[str]:
    """Get connector options for a role/intensity transition."""
    # Try exact match
    key = (from_role, to_role, intensity_trend)
    if key in CONNECTOR_MAP:
        return CONNECTOR_MAP[key]

    # Try with 'any' trend
    key_any = (from_role, to_role, "any")
    if key_any in CONNECTOR_MAP:
        return CONNECTOR_MAP[key_any]

    # Fallback
    return FALLBACK_CONNECTORS.get(intensity_trend, FALLBACK_CONNECTORS["flat"])
