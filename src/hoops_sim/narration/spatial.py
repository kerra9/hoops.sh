"""Spatial awareness for narration -- maps positions to natural language.

Converts Vec2 positions and Zone enums into broadcast-style court
location descriptions like 'at the top of the key', 'on the left wing',
'in the right corner', 'from the elbow', etc.
"""

from __future__ import annotations

import math
from typing import Optional, Tuple


# Court dimensions (half-court, feet)
_HALF_COURT_LENGTH = 47.0
_COURT_WIDTH = 50.0
_THREE_POINT_DISTANCE = 23.75
_RIM_X = 5.25  # distance from baseline to rim


class SpatialDescriber:
    """Maps court positions to natural-language descriptions.

    Uses the attacking direction flag to provide correct left/right
    orientation from the broadcast perspective.
    """

    # Zone name -> broadcast location phrase
    _ZONE_DESCRIPTIONS = {
        "restricted": "at the rim",
        "paint": "in the paint",
        "close_left": "on the left block",
        "close_right": "on the right block",
        "mid_left": "from the left side",
        "mid_right": "from the right side",
        "mid_top": "from the free throw line area",
        "elbow_left": "from the left elbow",
        "elbow_right": "from the right elbow",
        "free_throw": "at the free throw line",
        "three_left_corner": "from the left corner",
        "three_right_corner": "from the right corner",
        "three_left_wing": "from the left wing",
        "three_right_wing": "from the right wing",
        "three_top": "at the top of the key",
        "three_top_key": "at the top of the key",
        "deep_three": "from way downtown",
        "backcourt": "from his own half",
    }

    # Shorter versions for fragment composition
    _ZONE_SHORT = {
        "restricted": "the rim",
        "paint": "the paint",
        "close_left": "the left block",
        "close_right": "the right block",
        "mid_left": "the left side",
        "mid_right": "the right side",
        "elbow_left": "the left elbow",
        "elbow_right": "the right elbow",
        "free_throw": "the free throw line",
        "three_left_corner": "the left corner",
        "three_right_corner": "the right corner",
        "three_left_wing": "the left wing",
        "three_right_wing": "the right wing",
        "three_top": "the top of the key",
        "three_top_key": "the top of the key",
    }

    @classmethod
    def describe_location(cls, zone: str) -> str:
        """Get a full prepositional phrase for a zone name.

        Returns something like 'from the left wing' or 'at the rim'.
        """
        normalized = zone.lower().replace(" ", "_")
        return cls._ZONE_DESCRIPTIONS.get(normalized, f"from the {zone}")

    @classmethod
    def short_location(cls, zone: str) -> str:
        """Get a short noun phrase for a zone name.

        Returns something like 'the left wing' or 'the rim'.
        """
        normalized = zone.lower().replace(" ", "_")
        return cls._ZONE_SHORT.get(normalized, zone)

    @classmethod
    def describe_distance(cls, distance_ft: float) -> str:
        """Describe shot distance in broadcast style."""
        if distance_ft <= 4.0:
            return "at the rim"
        if distance_ft <= 8.0:
            return "from close range"
        if distance_ft <= 15.0:
            return "from the mid-range"
        if distance_ft <= 20.0:
            return f"from about {distance_ft:.0f} feet"
        if distance_ft <= 24.0:
            return f"from {distance_ft:.0f} feet"
        if distance_ft <= 28.0:
            return "from deep"
        return "from WAY downtown"

    @classmethod
    def describe_drive_direction(
        cls,
        start_x: float,
        start_y: float,
        end_x: float,
        end_y: float,
        attacking_right: bool = True,
    ) -> str:
        """Describe the direction of a drive.

        Uses the delta between start and end positions, adjusted
        for the attacking direction.
        """
        dx = end_x - start_x
        dy = end_y - start_y

        if not attacking_right:
            dx = -dx

        # Determine primary direction
        if abs(dy) > abs(dx) * 1.5:
            # Primarily lateral
            if dy > 0:
                return "left" if attacking_right else "right"
            return "right" if attacking_right else "left"

        # Check for baseline drive
        if dx > 0 and abs(dx) > abs(dy):
            if abs(dy) > 5.0:
                return "baseline" if (dy > 0) == attacking_right else "middle"
            return "to the basket"

        if dx < 0:
            return "pulls back"

        if dy > 0:
            return "left"
        return "right"

    @classmethod
    def shot_location_phrase(
        cls,
        zone: str,
        distance: float,
        is_three: bool,
    ) -> str:
        """Build a complete shot location phrase for broadcast.

        Combines zone and distance into a natural phrase like
        'from the left wing, 24 feet' or 'at the rim'.
        """
        if distance <= 4.0:
            return "at the rim"

        loc = cls.describe_location(zone)
        if is_three and distance > 26:
            return f"from deep, {distance:.0f} feet"
        if distance > 18:
            return f"{loc}, {distance:.0f} feet"
        return loc

    @classmethod
    def relative_position_phrase(
        cls,
        zone: str,
        previous_zone: Optional[str] = None,
    ) -> Optional[str]:
        """Generate a relative position phrase if relevant.

        Returns phrases like 'from the same spot' or None if no
        interesting relative context exists.
        """
        if previous_zone and previous_zone.lower() == zone.lower():
            return "from the same spot"
        return None
