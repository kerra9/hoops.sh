"""Situational basketball and clock management.

Adjusts player and team behavior based on game situation:
clutch time, end-of-quarter, trailing/leading, 2-for-1 opportunities.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class SituationType(enum.Enum):
    """Game situations that affect strategy."""

    NORMAL = "normal"
    CLUTCH = "clutch"
    GARBAGE_TIME = "garbage_time"
    TWO_FOR_ONE = "two_for_one"
    LAST_SHOT = "last_shot"
    HEAVE = "heave"
    INTENTIONAL_FOUL = "intentional_foul"
    MILK_CLOCK = "milk_clock"
    HURRY_UP = "hurry_up"


@dataclass
class SituationalModifiers:
    """Modifiers applied to player behavior in specific situations."""

    shot_volume_mod: float = 1.0
    iso_tendency_mod: float = 1.0
    three_point_tendency_mod: float = 1.0
    defensive_intensity_mod: float = 1.0
    pace_mod: float = 1.0
    gambling_mod: float = 1.0
    target_shot_clock: float = 14.0  # Ideal shot clock usage


def evaluate_situation(
    game_clock: float,
    shot_clock: float,
    quarter: int,
    score_diff: int,
    is_home: bool,
) -> tuple[SituationType, SituationalModifiers]:
    """Evaluate the game situation and return appropriate modifiers.

    Args:
        game_clock: Seconds remaining in the quarter.
        shot_clock: Seconds remaining on the shot clock.
        quarter: Current quarter (1-4+).
        score_diff: Score difference from this team's perspective (+ = leading).
        is_home: Whether this team is at home.

    Returns:
        Tuple of (situation type, modifiers).
    """
    # Heave: under 3 seconds, just chuck it
    if game_clock < 3.0 and game_clock > 0.0:
        return SituationType.HEAVE, SituationalModifiers(
            shot_volume_mod=2.0,
            three_point_tendency_mod=2.0,
            target_shot_clock=0.5,
        )

    # Last shot: hold for final possession
    if game_clock < 8.0 and game_clock >= 3.0:
        return SituationType.LAST_SHOT, SituationalModifiers(
            iso_tendency_mod=1.5,
            shot_volume_mod=1.3,
            target_shot_clock=max(1.0, game_clock - 2.0),
        )

    # 2-for-1: push for quick shot when 30-38 seconds left (end of half, Q4, or OT only)
    if 30.0 <= game_clock <= 38.0 and (quarter in (2, 4) or quarter > 4):
        return SituationType.TWO_FOR_ONE, SituationalModifiers(
            pace_mod=1.3,
            target_shot_clock=6.0,
        )

    # Clutch time: Q4 or OT, under 5 minutes, within 5 points
    if quarter >= 4 and game_clock < 300.0 and abs(score_diff) <= 5:
        return SituationType.CLUTCH, SituationalModifiers(
            shot_volume_mod=1.2,
            iso_tendency_mod=1.4,
            defensive_intensity_mod=1.3,
            gambling_mod=0.5,  # Less gambling on defense
            target_shot_clock=10.0,
        )

    # Intentional fouling: trailing by 3+ with < 30 seconds
    if quarter >= 4 and game_clock < 30.0 and score_diff < -3:
        return SituationType.INTENTIONAL_FOUL, SituationalModifiers(
            pace_mod=1.5,
            target_shot_clock=3.0,
        )

    # Milk clock: leading with < 2 minutes
    if quarter >= 4 and game_clock < 120.0 and score_diff > 3:
        return SituationType.MILK_CLOCK, SituationalModifiers(
            pace_mod=0.6,
            target_shot_clock=20.0,
            shot_volume_mod=0.7,
        )

    # Hurry up: trailing with < 2 minutes
    if quarter >= 4 and game_clock < 120.0 and score_diff < -3:
        return SituationType.HURRY_UP, SituationalModifiers(
            pace_mod=1.4,
            three_point_tendency_mod=1.5,
            target_shot_clock=8.0,
        )

    # Garbage time: Q4 and lead > 25
    if quarter >= 4 and abs(score_diff) > 25:
        return SituationType.GARBAGE_TIME, SituationalModifiers(
            shot_volume_mod=0.8,
            defensive_intensity_mod=0.7,
            gambling_mod=0.3,
        )

    return SituationType.NORMAL, SituationalModifiers()
