"""Spacing calculator from actual player positions."""

from __future__ import annotations

from typing import List

from hoops_sim.physics.vec import Vec2


def average_spacing(positions: List[Vec2]) -> float:
    """Calculate average distance between all pairs of players.

    Good spacing is typically 15-20 feet between players.
    Bad spacing (bunched up) is under 10 feet.

    Returns:
        Average distance in feet between all player pairs.
    """
    if len(positions) < 2:
        return 0.0

    total = 0.0
    count = 0
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            total += positions[i].distance_to(positions[j])
            count += 1

    return total / count if count > 0 else 0.0


def spacing_quality(positions: List[Vec2], basket_pos: Vec2) -> float:
    """Evaluate the quality of offensive spacing.

    Good spacing means:
    - Players are spread out (high average distance between each other)
    - Players are at varied distances from the basket (not all same distance)
    - No two players are too close together (< 6 feet)

    Returns:
        Quality score from 0.0 (terrible) to 1.0 (excellent).
    """
    if len(positions) < 2:
        return 0.5

    # Factor 1: Average spacing (ideal ~16 feet)
    avg = average_spacing(positions)
    spacing_score = min(1.0, avg / 18.0)  # Maxes out at 18 feet average

    # Factor 2: No bunching (penalize pairs closer than 6 feet)
    bunched_pairs = 0
    total_pairs = 0
    for i in range(len(positions)):
        for j in range(i + 1, len(positions)):
            total_pairs += 1
            if positions[i].distance_to(positions[j]) < 6.0:
                bunched_pairs += 1

    bunching_penalty = bunched_pairs / max(1, total_pairs)

    # Factor 3: Distance variety from basket
    distances = [p.distance_to(basket_pos) for p in positions]
    if len(distances) >= 2:
        dist_range = max(distances) - min(distances)
        variety_score = min(1.0, dist_range / 15.0)
    else:
        variety_score = 0.5

    return max(0.0, spacing_score * 0.5 + variety_score * 0.3 - bunching_penalty * 0.2)
