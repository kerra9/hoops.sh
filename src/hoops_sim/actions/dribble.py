"""Dribble move system with success probability and ankle-breaker mechanic."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.utils.rng import SeededRNG


class DribbleMoveType(enum.Enum):
    """Types of dribble moves."""

    CROSSOVER = "crossover"
    HESITATION = "hesitation"
    SPIN_MOVE = "spin_move"
    BEHIND_THE_BACK = "behind_the_back"
    STEP_BACK = "step_back"
    EURO_STEP = "euro_step"
    IN_AND_OUT = "in_and_out"
    # New moves added in the micro-action overhaul
    BETWEEN_THE_LEGS = "between_the_legs"
    SHAMGOD = "shamgod"
    SNATCH_BACK = "snatch_back"
    HARDEN_STEP_BACK = "harden_step_back"


@dataclass(frozen=True)
class DribbleMoveSpec:
    """Specification for a dribble move."""

    speed_boost: float  # Multiplier for speed after success
    space_created: float  # Feet of separation created
    turnover_risk: float  # Base turnover probability
    time_cost: float  # Seconds the move takes
    energy_cost: float  # Energy cost
    ankle_breaker_threshold: int  # Ball handle rating for ankle-breaker chance
    defender_freeze_time: float  # Seconds defender is frozen on success


DRIBBLE_MOVES: dict[DribbleMoveType, DribbleMoveSpec] = {
    DribbleMoveType.CROSSOVER: DribbleMoveSpec(
        speed_boost=1.15, space_created=2.0, turnover_risk=0.02,
        time_cost=0.4, energy_cost=0.03, ankle_breaker_threshold=92,
        defender_freeze_time=0.3,
    ),
    DribbleMoveType.HESITATION: DribbleMoveSpec(
        speed_boost=1.10, space_created=1.5, turnover_risk=0.01,
        time_cost=0.3, energy_cost=0.02, ankle_breaker_threshold=95,
        defender_freeze_time=0.2,
    ),
    DribbleMoveType.SPIN_MOVE: DribbleMoveSpec(
        speed_boost=1.05, space_created=2.5, turnover_risk=0.04,
        time_cost=0.5, energy_cost=0.04, ankle_breaker_threshold=88,
        defender_freeze_time=0.4,
    ),
    DribbleMoveType.BEHIND_THE_BACK: DribbleMoveSpec(
        speed_boost=1.08, space_created=2.0, turnover_risk=0.03,
        time_cost=0.4, energy_cost=0.03, ankle_breaker_threshold=90,
        defender_freeze_time=0.3,
    ),
    DribbleMoveType.STEP_BACK: DribbleMoveSpec(
        speed_boost=0.0, space_created=3.0, turnover_risk=0.02,
        time_cost=0.5, energy_cost=0.03, ankle_breaker_threshold=90,
        defender_freeze_time=0.3,
    ),
    DribbleMoveType.EURO_STEP: DribbleMoveSpec(
        speed_boost=1.0, space_created=2.0, turnover_risk=0.02,
        time_cost=0.6, energy_cost=0.04, ankle_breaker_threshold=88,
        defender_freeze_time=0.4,
    ),
    DribbleMoveType.IN_AND_OUT: DribbleMoveSpec(
        speed_boost=1.12, space_created=1.5, turnover_risk=0.02,
        time_cost=0.35, energy_cost=0.02, ankle_breaker_threshold=93,
        defender_freeze_time=0.25,
    ),
    # New moves added in the micro-action overhaul
    DribbleMoveType.BETWEEN_THE_LEGS: DribbleMoveSpec(
        speed_boost=1.08, space_created=1.5, turnover_risk=0.015,
        time_cost=0.35, energy_cost=0.02, ankle_breaker_threshold=94,
        defender_freeze_time=0.2,
    ),
    DribbleMoveType.SHAMGOD: DribbleMoveSpec(
        speed_boost=1.20, space_created=3.5, turnover_risk=0.08,
        time_cost=0.5, energy_cost=0.04, ankle_breaker_threshold=85,
        defender_freeze_time=0.5,
    ),
    DribbleMoveType.SNATCH_BACK: DribbleMoveSpec(
        speed_boost=0.0, space_created=2.5, turnover_risk=0.025,
        time_cost=0.4, energy_cost=0.03, ankle_breaker_threshold=90,
        defender_freeze_time=0.3,
    ),
    DribbleMoveType.HARDEN_STEP_BACK: DribbleMoveSpec(
        speed_boost=0.0, space_created=4.0, turnover_risk=0.03,
        time_cost=0.6, energy_cost=0.04, ankle_breaker_threshold=88,
        defender_freeze_time=0.4,
    ),
}


@dataclass
class DribbleMoveResult:
    """Result of attempting a dribble move."""

    success: bool
    separation: float = 0.0  # Feet of separation gained
    turnover: bool = False
    ankle_breaker: bool = False
    energy_cost: float = 0.0


def resolve_dribble_move(
    ball_handle: int,
    energy_pct: float,
    defender_lateral: int,
    defender_steal: int,
    move_type: DribbleMoveType,
    has_ankle_breaker_badge: bool,
    badge_tier: int,
    rng: SeededRNG,
) -> DribbleMoveResult:
    """Resolve a dribble move attempt.

    Args:
        ball_handle: Ball handler's ball handling rating (0-99).
        energy_pct: Ball handler's energy percentage (0-1).
        defender_lateral: Defender's lateral quickness (0-99).
        defender_steal: Defender's steal rating (0-99).
        move_type: Type of dribble move.
        has_ankle_breaker_badge: Whether the ball handler has the ankle breaker badge.
        badge_tier: Ankle breaker badge tier (0-4).
        rng: Random number generator.

    Returns:
        DribbleMoveResult with outcome.
    """
    spec = DRIBBLE_MOVES[move_type]

    # Base success probability from ball handling
    success_prob = ball_handle / 100.0
    success_prob *= energy_pct  # Fatigue reduces effectiveness
    success_prob -= defender_lateral / 200.0  # Defender resistance
    success_prob = max(0.05, min(0.95, success_prob))  # Clamp to [5%, 95%]

    if rng.random() < success_prob:
        # Move succeeded
        separation = spec.speed_boost * 2 + spec.space_created

        # Ankle-breaker check
        ankle_breaker = False
        if ball_handle >= spec.ankle_breaker_threshold:
            ab_chance = (ball_handle - spec.ankle_breaker_threshold) * 0.01
            if has_ankle_breaker_badge:
                ab_chance += badge_tier * 0.02
            if rng.random() < ab_chance:
                ankle_breaker = True
                separation *= 2.5

        return DribbleMoveResult(
            success=True,
            separation=separation,
            ankle_breaker=ankle_breaker,
            energy_cost=spec.energy_cost,
        )
    else:
        # Move failed
        if rng.random() < spec.turnover_risk * (1 + defender_steal / 100.0):
            return DribbleMoveResult(
                success=False, turnover=True, energy_cost=spec.energy_cost * 0.5,
            )
        return DribbleMoveResult(success=False, energy_cost=spec.energy_cost * 0.5)
