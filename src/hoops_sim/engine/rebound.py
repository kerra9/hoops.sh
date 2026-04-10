"""Micro-action rebound simulation.

After a missed shot, players compete for the rebound based on
positioning, box-out status, height, vertical leap, and hustle.
The ball trajectory determines where the rebound lands.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


class ReboundType(enum.Enum):
    """Where the miss bounces."""

    SHORT = "short"  # Front rim, near the basket
    LONG = "long"  # Back iron, free-throw line area
    SIDE = "side"  # Air ball or side bounce
    RIM_OUT = "rim_out"  # Can go anywhere


@dataclass
class ReboundCandidate:
    """A player competing for a rebound."""

    player_id: int
    position: Vec2
    height_inches: int
    vertical_leap: int
    rebound_rating: int
    box_out_rating: int
    hustle: int
    is_boxed_out: bool
    is_offense: bool
    crash_boards_tendency: float


@dataclass
class ReboundResult:
    """Result of a rebound competition."""

    rebounder_id: int
    is_offensive_rebound: bool
    rebound_position: Vec2
    was_contested: bool


def determine_rebound_location(
    shot_distance: float,
    is_three: bool,
    rim_result: str,
    basket_position: Vec2,
    rng: SeededRNG,
) -> tuple[ReboundType, Vec2]:
    """Determine where the missed shot bounces.

    Args:
        shot_distance: Distance of the shot attempt.
        is_three: Whether it was a three-pointer.
        rim_result: How the ball hit the rim (front, back, side, air_ball).
        basket_position: Position of the basket.
        rng: Random number generator.

    Returns:
        Tuple of (rebound type, landing position).
    """
    if rim_result == "air_ball":
        angle = rng.uniform(0, 360)
        dist = rng.uniform(3, 8)
        offset = Vec2.from_angle(angle) * dist
        return ReboundType.SIDE, basket_position + offset

    if rim_result == "front":
        # Short miss: near the basket
        offset = Vec2(rng.gauss(0, 2), rng.gauss(0, 2))
        return ReboundType.SHORT, basket_position + offset

    if rim_result == "back":
        # Long miss: bounces out toward FT line
        if is_three:
            dist = rng.uniform(8, 15)
        else:
            dist = rng.uniform(5, 12)
        angle = rng.uniform(-45, 45)
        offset = Vec2.from_angle(angle) * dist
        return ReboundType.LONG, basket_position + offset

    # Rim out: random direction
    dist = rng.uniform(2, 10)
    angle = rng.uniform(0, 360)
    offset = Vec2.from_angle(angle) * dist
    return ReboundType.RIM_OUT, basket_position + offset


def resolve_rebound(
    candidates: list[ReboundCandidate],
    rebound_position: Vec2,
    rebound_type: ReboundType,
    rng: SeededRNG,
) -> ReboundResult | None:
    """Resolve who gets the rebound.

    Args:
        candidates: Players competing for the rebound.
        rebound_position: Where the ball is landing.
        rebound_type: Type of rebound.
        rng: Random number generator.

    Returns:
        ReboundResult or None if no one gets it (out of bounds).
    """
    if not candidates:
        return None

    scored: list[tuple[ReboundCandidate, float]] = []

    for cand in candidates:
        dist = cand.position.distance_to(rebound_position)
        if dist > 15.0:
            continue  # Too far away

        # Position advantage (closer = better)
        position_score = max(0, 1.0 - dist / 12.0)

        # Height + vertical = reach advantage
        reach = (cand.height_inches + cand.vertical_leap * 0.4) / 100.0

        # Rebound skill
        reb_skill = cand.rebound_rating / 99.0

        # Box-out effect
        box_out_penalty = 0.6 if cand.is_boxed_out else 1.0

        # Hustle for second efforts
        hustle_bonus = cand.hustle / 99.0 * 0.15

        # Offensive vs defensive base
        if cand.is_offense:
            base = 0.27 * cand.crash_boards_tendency  # OREB% base
        else:
            base = 0.73  # DREB% base

        score = (
            position_score * 0.30
            + reach * 0.20
            + reb_skill * 0.25
            + hustle_bonus
            + base * 0.10
        ) * box_out_penalty

        score += rng.gauss(0, 0.08)
        scored.append((cand, max(0.01, score)))

    if not scored:
        return None

    # Weighted random selection
    total = sum(s for _, s in scored)
    roll = rng.random() * total
    cumulative = 0.0
    winner = scored[0]
    for cand, score in scored:
        cumulative += score
        if roll <= cumulative:
            winner = (cand, score)
            break

    rebounder = winner[0]
    return ReboundResult(
        rebounder_id=rebounder.player_id,
        is_offensive_rebound=rebounder.is_offense,
        rebound_position=rebound_position,
        was_contested=len(scored) > 1,
    )
