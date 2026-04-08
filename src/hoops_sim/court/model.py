"""Court spatial model with dimensions and coordinate system.

The court uses a coordinate system where:
- x runs along the length (0 = left baseline, 94 = right baseline)
- y runs along the width (0 = bottom sideline, 50 = top sideline)
- The LEFT basket is at (5.25, 25.0) and the RIGHT basket is at (88.75, 25.0)
"""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    BASKET_X,
    BASKET_Y,
    COURT_LENGTH,
    COURT_WIDTH,
    FREE_THROW_DISTANCE,
    HALF_COURT_LENGTH,
    PAINT_LENGTH,
    RESTRICTED_AREA_RADIUS,
    THREE_POINT_ARC_DISTANCE,
    THREE_POINT_CORNER_DISTANCE,
)


# Basket positions for each side of the court
LEFT_BASKET = Vec2(BASKET_X, BASKET_Y)
RIGHT_BASKET = Vec2(COURT_LENGTH - BASKET_X, BASKET_Y)


@dataclass(frozen=True)
class CourtDimensions:
    """NBA court dimensions."""

    length: float = COURT_LENGTH
    width: float = COURT_WIDTH
    half_court: float = HALF_COURT_LENGTH
    three_point_arc: float = THREE_POINT_ARC_DISTANCE
    three_point_corner: float = THREE_POINT_CORNER_DISTANCE
    free_throw_distance: float = FREE_THROW_DISTANCE
    paint_length: float = PAINT_LENGTH
    restricted_area_radius: float = RESTRICTED_AREA_RADIUS


def is_in_bounds(position: Vec2) -> bool:
    """Check if a position is within the court boundaries."""
    return 0.0 <= position.x <= COURT_LENGTH and 0.0 <= position.y <= COURT_WIDTH


def is_in_frontcourt(position: Vec2, attacking_right: bool) -> bool:
    """Check if a position is in the frontcourt for the attacking team.

    Args:
        position: Court position.
        attacking_right: True if the team is attacking the right basket.
    """
    if attacking_right:
        return position.x >= HALF_COURT_LENGTH
    return position.x <= HALF_COURT_LENGTH


def get_basket_position(attacking_right: bool) -> Vec2:
    """Get the basket position for the attacking team."""
    return RIGHT_BASKET if attacking_right else LEFT_BASKET


def distance_to_basket(position: Vec2, attacking_right: bool) -> float:
    """Distance from a position to the basket the team is attacking."""
    basket = get_basket_position(attacking_right)
    return position.distance_to(basket)


def is_in_paint(position: Vec2, attacking_right: bool) -> bool:
    """Check if a position is inside the paint (key/lane).

    The paint is a rectangle from the baseline to 19 feet out,
    and 16 feet wide (8 feet on each side of the basket).
    """
    basket = get_basket_position(attacking_right)
    if attacking_right:
        # Paint is from the right baseline inward
        x_in_paint = position.x >= (COURT_LENGTH - PAINT_LENGTH)
    else:
        # Paint is from the left baseline inward
        x_in_paint = position.x <= PAINT_LENGTH

    y_in_paint = abs(position.y - basket.y) <= 8.0  # 16 feet wide / 2
    return x_in_paint and y_in_paint


def is_in_restricted_area(position: Vec2, attacking_right: bool) -> bool:
    """Check if a position is inside the restricted area (4-foot arc under the basket)."""
    basket = get_basket_position(attacking_right)
    return position.distance_to(basket) <= RESTRICTED_AREA_RADIUS


def is_three_point(position: Vec2, attacking_right: bool) -> bool:
    """Check if a position is beyond the three-point line.

    The three-point line is an arc at 23.75 feet from the basket center,
    with straight lines in the corners at 22 feet from the basket.
    """
    basket = get_basket_position(attacking_right)
    dist = position.distance_to(basket)

    # In the corners, the three-point line is 22 feet (straight line, not arc)
    if position.y <= 3.0 or position.y >= COURT_WIDTH - 3.0:
        return dist >= THREE_POINT_CORNER_DISTANCE

    return dist >= THREE_POINT_ARC_DISTANCE
