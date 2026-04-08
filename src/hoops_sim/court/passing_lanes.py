"""Passing lane geometry: line-of-sight with defender obstruction."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List

from hoops_sim.physics.vec import Vec2


@dataclass
class PassingLaneResult:
    """Result of a passing lane analysis."""

    open: bool  # Whether the lane is clear
    quality: float  # 0-1: how clear the lane is
    closest_defender_distance: float  # Feet from the passing lane
    interception_risk: float  # 0-1: probability of a steal


def point_to_segment_distance(point: Vec2, seg_start: Vec2, seg_end: Vec2) -> float:
    """Calculate the perpendicular distance from a point to a line segment.

    Args:
        point: The point to measure from.
        seg_start: Start of the line segment.
        seg_end: End of the line segment.

    Returns:
        Distance in feet.
    """
    seg = seg_end - seg_start
    seg_len_sq = seg.magnitude_squared()
    if seg_len_sq < 0.01:
        return point.distance_to(seg_start)

    # Project point onto the segment line, clamped to [0, 1]
    t = max(0.0, min(1.0, (point - seg_start).dot(seg) / seg_len_sq))
    projection = seg_start + seg * t
    return point.distance_to(projection)


def analyze_passing_lane(
    passer_pos: Vec2,
    receiver_pos: Vec2,
    defender_positions: List[Vec2],
    pass_lane_width: float = 2.5,
) -> PassingLaneResult:
    """Analyze whether a passing lane is open.

    Checks if any defender is close enough to the passing lane
    to intercept or deflect the pass.

    Args:
        passer_pos: Position of the passer.
        receiver_pos: Position of the intended receiver.
        defender_positions: Positions of all defenders.
        pass_lane_width: Width of the passing lane in feet.

    Returns:
        PassingLaneResult with lane quality and interception risk.
    """
    if not defender_positions:
        return PassingLaneResult(open=True, quality=1.0, closest_defender_distance=99.0, interception_risk=0.0)

    pass_distance = passer_pos.distance_to(receiver_pos)
    closest = 99.0

    for def_pos in defender_positions:
        dist = point_to_segment_distance(def_pos, passer_pos, receiver_pos)
        closest = min(closest, dist)

    # Quality based on closest defender distance
    if closest > pass_lane_width * 2:
        quality = 1.0
    elif closest > pass_lane_width:
        quality = 0.5 + (closest - pass_lane_width) / (pass_lane_width * 2)
    else:
        quality = max(0.0, closest / pass_lane_width * 0.5)

    # Interception risk
    if closest < 1.5:
        interception_risk = 0.15 + (1.5 - closest) * 0.15
    elif closest < 3.0:
        interception_risk = 0.05
    else:
        interception_risk = 0.01

    # Longer passes are riskier
    interception_risk *= min(2.0, pass_distance / 15.0)

    is_open = closest > pass_lane_width

    return PassingLaneResult(
        open=is_open,
        quality=quality,
        closest_defender_distance=closest,
        interception_risk=min(0.5, interception_risk),
    )
