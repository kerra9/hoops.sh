"""Passing system: all pass types with interception probability."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


class PassType(enum.Enum):
    """Types of passes."""

    CHEST = "chest"
    BOUNCE = "bounce"
    OVERHEAD = "overhead"
    LOB = "lob"
    BULLET = "bullet"
    BEHIND_BACK = "behind_back"
    NO_LOOK = "no_look"
    ALLEY_OOP = "alley_oop"


@dataclass
class PassResult:
    """Result of a pass attempt."""

    completed: bool
    intercepted: bool = False
    deflected: bool = False
    turnover: bool = False
    receiver_catch_difficulty: float = 0.0  # 0-1: how hard the catch is


def resolve_pass(
    pass_accuracy: int,
    pass_vision: int,
    receiver_hands: int,
    pass_type: PassType,
    distance: float,
    lane_quality: float,
    is_under_pressure: bool,
    has_needle_threader: bool,
    has_bail_out: bool,
    rng: SeededRNG,
) -> PassResult:
    """Resolve a pass attempt.

    Args:
        pass_accuracy: Passer's pass accuracy rating (0-99).
        pass_vision: Passer's pass vision rating (0-99).
        receiver_hands: Receiver's hands rating (0-99).
        pass_type: Type of pass.
        distance: Distance of the pass in feet.
        lane_quality: How open the passing lane is (0-1).
        is_under_pressure: Whether the passer is being pressured.
        has_needle_threader: Passer has the needle threader badge.
        has_bail_out: Passer has the bail out badge.
        rng: Random number generator.

    Returns:
        PassResult with outcome.
    """
    # Base completion probability
    base = pass_accuracy / 100.0

    # Distance penalty: longer passes are harder
    distance_factor = max(0.7, 1.0 - distance / 80.0)
    base *= distance_factor

    # Lane quality: open lanes are easier
    lane_factor = 0.5 + lane_quality * 0.5
    base *= lane_factor

    # Pass type difficulty modifiers
    type_mods = {
        PassType.CHEST: 1.0,
        PassType.BOUNCE: 0.95,
        PassType.OVERHEAD: 0.90,
        PassType.LOB: 0.85,
        PassType.BULLET: 0.92,
        PassType.BEHIND_BACK: 0.80,
        PassType.NO_LOOK: 0.75,
        PassType.ALLEY_OOP: 0.70,
    }
    base *= type_mods.get(pass_type, 1.0)

    # Pressure penalty
    if is_under_pressure:
        if has_bail_out:
            base *= 0.95  # Badge mitigates pressure
        else:
            base *= 0.85

    # Needle threader badge helps tight lanes
    if has_needle_threader and lane_quality < 0.5:
        base *= 1.10

    base = max(0.1, min(0.99, base))

    if rng.random() < base:
        # Pass completed
        catch_diff = max(0.0, 1.0 - receiver_hands / 100.0) * 0.5
        return PassResult(completed=True, receiver_catch_difficulty=catch_diff)
    else:
        # Pass failed
        if lane_quality < 0.4 and rng.random() < 0.4:
            return PassResult(completed=False, intercepted=True, turnover=True)
        if rng.random() < 0.3:
            return PassResult(completed=False, deflected=True, turnover=True)
        return PassResult(completed=False, turnover=True)
