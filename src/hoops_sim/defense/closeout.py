"""Closeout mechanics: how defenders sprint to contest shooters.

When a pass reaches a perimeter player, their defender must close out.
The quality of the closeout determines whether the shooter gets an open
look, a contested shot, or a driving opportunity from a hard closeout.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


class CloseoutType(enum.Enum):
    """Types of closeouts."""

    HARD = "hard"  # Sprint at full speed, can't stop
    CONTROLLED = "controlled"  # Slower but maintains balance
    LATE = "late"  # Too far away, arrives after the shot
    NO_CLOSEOUT = "no_closeout"  # Defender doesn't close out


@dataclass
class CloseoutResult:
    """Result of a closeout attempt."""

    closeout_type: CloseoutType
    contest_quality: float = 0.0  # 0-1, how well the shot is contested
    can_be_pump_faked: bool = False  # Defender overcommitted?
    arriving_distance: float = 10.0  # How close the defender gets


def evaluate_closeout(
    defender_position: Vec2,
    shooter_position: Vec2,
    defender_speed: int,
    defender_lateral: int,
    closeout_aggression: float,
    time_available_ticks: int,
    rng: SeededRNG,
) -> CloseoutResult:
    """Evaluate a closeout attempt.

    Args:
        defender_position: Defender's current position.
        shooter_position: Shooter's position.
        defender_speed: Defender's speed attribute (0-99).
        defender_lateral: Defender's lateral quickness (0-99).
        closeout_aggression: Defender's closeout aggression tendency (0-1).
        time_available_ticks: How many ticks before the shooter releases.
        rng: Random number generator.

    Returns:
        CloseoutResult with the outcome.
    """
    distance = defender_position.distance_to(shooter_position)

    # How fast can the defender cover ground?
    # Speed attribute maps to ~18-28 ft/s, at 0.1s per tick
    speed_fps = 18.0 + (defender_speed / 99.0) * 10.0
    ground_per_tick = speed_fps * 0.1  # feet per tick
    max_cover = ground_per_tick * time_available_ticks

    if max_cover < distance * 0.5:
        # Can't get there in time
        return CloseoutResult(
            closeout_type=CloseoutType.NO_CLOSEOUT,
            contest_quality=0.05,
            arriving_distance=distance - max_cover,
        )

    if max_cover < distance * 0.8:
        # Late closeout
        arriving_dist = max(2.0, distance - max_cover)
        contest = max(0.0, 0.4 - arriving_dist * 0.05)
        return CloseoutResult(
            closeout_type=CloseoutType.LATE,
            contest_quality=contest,
            arriving_distance=arriving_dist,
        )

    # Defender can get there -- choose between hard and controlled
    is_hard = closeout_aggression > 0.6 or (
        closeout_aggression > 0.3 and rng.random() < 0.5
    )

    if is_hard:
        # Hard closeout: better contest but vulnerable to pump fakes
        contest = 0.7 + (defender_lateral / 99.0) * 0.2
        can_be_faked = rng.random() < 0.3 + closeout_aggression * 0.2
        return CloseoutResult(
            closeout_type=CloseoutType.HARD,
            contest_quality=min(1.0, contest + rng.gauss(0, 0.05)),
            can_be_pump_faked=can_be_faked,
            arriving_distance=1.5,
        )
    else:
        # Controlled closeout: less contest but maintains position
        contest = 0.4 + (defender_lateral / 99.0) * 0.2
        return CloseoutResult(
            closeout_type=CloseoutType.CONTROLLED,
            contest_quality=min(1.0, contest + rng.gauss(0, 0.05)),
            can_be_pump_faked=False,
            arriving_distance=3.0,
        )
