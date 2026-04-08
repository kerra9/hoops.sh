"""Driving lane analyzer: path to rim with help positions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from hoops_sim.physics.vec import Vec2


@dataclass
class DrivingLaneResult:
    """Result of driving lane analysis."""

    open: bool  # Whether the lane to the rim is clear
    quality: float  # 0-1: how open the lane is
    help_defenders_in_path: int  # Number of help defenders near the path
    closest_help_distance: float  # Feet from the nearest help defender


def analyze_driving_lane(
    driver_pos: Vec2,
    basket_pos: Vec2,
    primary_defender_pos: Vec2,
    help_defender_positions: List[Vec2],
    lane_width: float = 4.0,
) -> DrivingLaneResult:
    """Analyze whether a driving lane to the basket is open.

    Considers the primary defender's position and help defenders
    along the path to the rim.

    Args:
        driver_pos: Position of the ball handler.
        basket_pos: The basket being attacked.
        primary_defender_pos: Position of the on-ball defender.
        help_defender_positions: Positions of help-side defenders.
        lane_width: Width of the driving corridor in feet.

    Returns:
        DrivingLaneResult with lane quality.
    """
    from hoops_sim.court.passing_lanes import point_to_segment_distance

    drive_direction = basket_pos - driver_pos
    drive_distance = drive_direction.magnitude()
    if drive_distance < 1.0:
        return DrivingLaneResult(open=True, quality=1.0, help_defenders_in_path=0, closest_help_distance=99.0)

    # Check primary defender position
    # Is the defender between the driver and the basket?
    def_dist = point_to_segment_distance(primary_defender_pos, driver_pos, basket_pos)
    primary_blocking = def_dist < lane_width

    # Check help defenders
    help_in_path = 0
    closest_help = 99.0
    for help_pos in help_defender_positions:
        dist = point_to_segment_distance(help_pos, driver_pos, basket_pos)
        closest_help = min(closest_help, dist)
        if dist < lane_width * 1.5:  # Help defenders have wider influence
            help_in_path += 1

    # Quality calculation
    if primary_blocking and help_in_path >= 2:
        quality = 0.1  # Very clogged lane
    elif primary_blocking and help_in_path >= 1:
        quality = 0.25
    elif primary_blocking:
        quality = 0.4  # Only primary defender, no help
    elif help_in_path >= 2:
        quality = 0.3
    elif help_in_path >= 1:
        quality = 0.55
    else:
        quality = 0.9  # Wide open lane

    # Adjust for closest help distance
    if closest_help > 10.0:
        quality = min(1.0, quality + 0.1)

    is_open = quality >= 0.5

    return DrivingLaneResult(
        open=is_open,
        quality=quality,
        help_defenders_in_path=help_in_path,
        closest_help_distance=closest_help,
    )
