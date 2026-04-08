"""17 shooting zones with polygon boundaries.

The court is divided into 17 zones for shot tracking and hot/cold zone analysis.
All zones are defined relative to a single basket (attacking right). When attacking
left, positions are mirrored.

Zone layout (attacking right basket at x=88.75, y=25):
  - Zone 0: Restricted area (under basket)
  - Zones 1-4: Close range (inside paint, outside restricted)
  - Zones 5-9: Mid-range areas
  - Zones 10-13: Three-point arc segments
  - Zones 14-15: Corner threes
  - Zone 16: Deep three / half-court+
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import IntEnum
from typing import Dict

from hoops_sim.court.model import (
    RIGHT_BASKET,
    get_basket_position,
    is_in_restricted_area,
    is_three_point,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    COURT_LENGTH,
    COURT_WIDTH,
    FREE_THROW_DISTANCE,
    HALF_COURT_LENGTH,
    RESTRICTED_AREA_RADIUS,
    THREE_POINT_ARC_DISTANCE,
)


class Zone(IntEnum):
    """Court shooting zones."""

    RESTRICTED = 0

    # Close range (inside paint, outside restricted area)
    CLOSE_LEFT = 1
    CLOSE_MIDDLE = 2
    CLOSE_RIGHT = 3
    CLOSE_BASELINE = 4

    # Mid-range
    MID_LEFT_WING = 5
    MID_LEFT_ELBOW = 6
    MID_FREE_THROW = 7
    MID_RIGHT_ELBOW = 8
    MID_RIGHT_WING = 9

    # Three-point arc
    THREE_LEFT_WING = 10
    THREE_LEFT_ABOVE_BREAK = 11
    THREE_TOP_KEY = 12
    THREE_RIGHT_ABOVE_BREAK = 13

    # Corner threes
    THREE_LEFT_CORNER = 14
    THREE_RIGHT_CORNER = 15

    # Deep
    DEEP_THREE = 16


@dataclass(frozen=True)
class ZoneInfo:
    """Information about a shooting zone."""

    zone: Zone
    name: str
    short_name: str
    is_three: bool
    is_paint: bool
    avg_distance: float  # Average distance to basket in feet


# Zone metadata
ZONE_INFO: Dict[Zone, ZoneInfo] = {
    Zone.RESTRICTED: ZoneInfo(Zone.RESTRICTED, "Restricted Area", "RA", False, True, 2.0),
    Zone.CLOSE_LEFT: ZoneInfo(Zone.CLOSE_LEFT, "Close Left", "CL", False, True, 6.0),
    Zone.CLOSE_MIDDLE: ZoneInfo(Zone.CLOSE_MIDDLE, "Close Middle", "CM", False, True, 7.0),
    Zone.CLOSE_RIGHT: ZoneInfo(Zone.CLOSE_RIGHT, "Close Right", "CR", False, True, 6.0),
    Zone.CLOSE_BASELINE: ZoneInfo(Zone.CLOSE_BASELINE, "Close Baseline", "CB", False, True, 5.0),
    Zone.MID_LEFT_WING: ZoneInfo(Zone.MID_LEFT_WING, "Mid Left Wing", "MLW", False, False, 16.0),
    Zone.MID_LEFT_ELBOW: ZoneInfo(Zone.MID_LEFT_ELBOW, "Mid Left Elbow", "MLE", False, False, 15.0),
    Zone.MID_FREE_THROW: ZoneInfo(Zone.MID_FREE_THROW, "Mid Free Throw", "MFT", False, False, 15.0),
    Zone.MID_RIGHT_ELBOW: ZoneInfo(Zone.MID_RIGHT_ELBOW, "Mid Right Elbow", "MRE", False, False, 15.0),
    Zone.MID_RIGHT_WING: ZoneInfo(Zone.MID_RIGHT_WING, "Mid Right Wing", "MRW", False, False, 16.0),
    Zone.THREE_LEFT_WING: ZoneInfo(Zone.THREE_LEFT_WING, "Three Left Wing", "3LW", True, False, 24.0),
    Zone.THREE_LEFT_ABOVE_BREAK: ZoneInfo(Zone.THREE_LEFT_ABOVE_BREAK, "Three Left Above Break", "3LA", True, False, 24.0),
    Zone.THREE_TOP_KEY: ZoneInfo(Zone.THREE_TOP_KEY, "Three Top of Key", "3TK", True, False, 24.5),
    Zone.THREE_RIGHT_ABOVE_BREAK: ZoneInfo(Zone.THREE_RIGHT_ABOVE_BREAK, "Three Right Above Break", "3RA", True, False, 24.0),
    Zone.THREE_LEFT_CORNER: ZoneInfo(Zone.THREE_LEFT_CORNER, "Left Corner Three", "LC3", True, False, 22.0),
    Zone.THREE_RIGHT_CORNER: ZoneInfo(Zone.THREE_RIGHT_CORNER, "Right Corner Three", "RC3", True, False, 22.0),
    Zone.DEEP_THREE: ZoneInfo(Zone.DEEP_THREE, "Deep Three", "D3", True, False, 28.0),
}


def get_zone(position: Vec2, attacking_right: bool) -> Zone:
    """Determine which shooting zone a court position falls in.

    Args:
        position: Position on the court.
        attacking_right: True if attacking the right basket.

    Returns:
        The Zone the position is in.
    """
    basket = get_basket_position(attacking_right)
    dist = position.distance_to(basket)

    # Deep three: beyond 28 feet or past half court
    if dist > 28.0 or (attacking_right and position.x < HALF_COURT_LENGTH) or (
        not attacking_right and position.x > HALF_COURT_LENGTH
    ):
        return Zone.DEEP_THREE

    # Angle from basket to position (relative to the baseline direction)
    dx = position.x - basket.x
    dy = position.y - basket.y
    # For attacking right, shots come from the left (negative dx is toward shooter)
    # Flip dx so angle is measured from the direction facing the shooter
    if attacking_right:
        dx = -dx
    angle = math.degrees(math.atan2(dy, dx))  # -180 to 180

    # Restricted area
    if is_in_restricted_area(position, attacking_right):
        return Zone.RESTRICTED

    # Three-point range
    if is_three_point(position, attacking_right):
        # Corner threes (bottom of court = right corner when attacking right)
        if position.y <= 3.0:
            return Zone.THREE_RIGHT_CORNER if attacking_right else Zone.THREE_LEFT_CORNER
        if position.y >= COURT_WIDTH - 3.0:
            return Zone.THREE_LEFT_CORNER if attacking_right else Zone.THREE_RIGHT_CORNER

        # Arc segments based on angle
        if angle > 60:
            return Zone.THREE_LEFT_WING
        if angle > 20:
            return Zone.THREE_LEFT_ABOVE_BREAK
        if angle > -20:
            return Zone.THREE_TOP_KEY
        if angle > -60:
            return Zone.THREE_RIGHT_ABOVE_BREAK
        return Zone.THREE_LEFT_WING  # Wraps around

    # Close range (inside ~10 feet, outside restricted)
    if dist <= 10.0:
        if angle > 45:
            return Zone.CLOSE_LEFT
        if angle > -45:
            return Zone.CLOSE_MIDDLE
        if angle > -90:
            return Zone.CLOSE_RIGHT
        return Zone.CLOSE_BASELINE

    # Mid-range
    if angle > 50:
        return Zone.MID_LEFT_WING
    if angle > 20:
        return Zone.MID_LEFT_ELBOW
    if angle > -20:
        return Zone.MID_FREE_THROW
    if angle > -50:
        return Zone.MID_RIGHT_ELBOW
    return Zone.MID_RIGHT_WING


def get_zone_info(zone: Zone) -> ZoneInfo:
    """Get metadata about a zone."""
    return ZONE_INFO[zone]
