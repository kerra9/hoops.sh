"""18-factor shot probability calculator.

Determines the probability of a shot going in based on the shooter's
attributes, defensive context, game situation, and other factors.
"""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.utils.math import clamp


@dataclass
class ShotContext:
    """All contextual factors for a shot attempt."""

    # Shooter factors
    base_rating: int = 50  # Zone-adjusted shooting rating (0-99)
    energy_pct: float = 1.0  # Shooter's energy (0-1)
    is_open: bool = True  # Whether the shooter is open
    is_catch_and_shoot: bool = False  # Caught and immediately shot
    is_off_dribble: bool = False  # Created own shot off the dribble
    hot_cold_modifier: float = 0.0  # Hot/cold streak modifier (-0.1 to +0.1)
    shot_distance: float = 15.0  # Distance to basket in feet

    # Defense factors
    contest_distance: float = 6.0  # Closest defender distance (feet)
    contest_quality: float = 0.0  # 0-1: how well contested (0=open, 1=smothered)
    rim_protector_present: bool = False  # Is a rim protector nearby?

    # Badge modifiers
    deadeye_tier: int = 0  # Reduces contest penalty (0-4)
    catch_and_shoot_tier: int = 0  # Boosts catch-and-shoot (0-4)
    hot_zone_hunter_tier: int = 0  # Boosts shots from hot zones (0-4)
    corner_specialist_tier: int = 0  # Boosts corner threes (0-4)
    volume_shooter_tier: int = 0  # Gets better with more attempts (0-4)

    # Situation
    is_clutch: bool = False
    clutch_rating: int = 50  # Shooter's clutch attribute
    is_hot_zone: bool = False  # Shooting from a personal hot zone
    is_corner_three: bool = False
    shot_attempts_this_game: int = 0  # For volume shooter badge


def calculate_shot_probability(ctx: ShotContext) -> float:
    """Calculate the probability of a shot going in.

    Uses 18 factors to determine the final make probability.

    Args:
        ctx: Shot context with all relevant factors.

    Returns:
        Probability from 0.0 to 1.0.
    """
    # Factor 1: Base rating (most important factor)
    base = ctx.base_rating / 100.0

    # Factor 2: Distance decay (further = harder)
    if ctx.shot_distance <= 4.0:
        distance_mod = 1.15  # At the rim, slightly boosted
    elif ctx.shot_distance <= 15.0:
        distance_mod = 1.0 - (ctx.shot_distance - 4.0) * 0.008
    else:
        distance_mod = 0.91 - (ctx.shot_distance - 15.0) * 0.005
    distance_mod = max(0.6, distance_mod)

    # Factor 3: Contest penalty
    contest_penalty = 1.0 - ctx.contest_quality * 0.35
    # Deadeye badge reduces contest penalty
    if ctx.deadeye_tier > 0:
        badge_reduction = ctx.deadeye_tier * 0.03
        contest_penalty = min(1.0, contest_penalty + badge_reduction)

    # Factor 4: Energy/fatigue
    fatigue_mod = 0.85 + ctx.energy_pct * 0.15  # 0.85 to 1.0

    # Factor 5: Catch-and-shoot bonus
    cas_bonus = 1.0
    if ctx.is_catch_and_shoot:
        cas_bonus = 1.03 + ctx.catch_and_shoot_tier * 0.01

    # Factor 6: Off-dribble penalty
    dribble_mod = 0.92 if ctx.is_off_dribble else 1.0

    # Factor 7: Hot/cold streak
    streak_mod = 1.0 + ctx.hot_cold_modifier

    # Factor 8: Rim protector deterrent
    rim_mod = 0.92 if ctx.rim_protector_present and ctx.shot_distance < 8.0 else 1.0

    # Factor 9: Hot zone bonus
    hz_bonus = 1.0
    if ctx.is_hot_zone and ctx.hot_zone_hunter_tier > 0:
        hz_bonus = 1.02 + ctx.hot_zone_hunter_tier * 0.01

    # Factor 10: Corner specialist
    corner_bonus = 1.0
    if ctx.is_corner_three and ctx.corner_specialist_tier > 0:
        corner_bonus = 1.02 + ctx.corner_specialist_tier * 0.01

    # Factor 11: Clutch modifier
    clutch_mod = 1.0
    if ctx.is_clutch:
        clutch_factor = (ctx.clutch_rating - 50) / 500.0  # -0.1 to +0.1
        clutch_mod = 1.0 + clutch_factor

    # Factor 12: Volume shooter badge
    volume_bonus = 1.0
    if ctx.volume_shooter_tier > 0 and ctx.shot_attempts_this_game > 8:
        volume_bonus = 1.0 + ctx.volume_shooter_tier * 0.005 * min(5, ctx.shot_attempts_this_game - 8)

    # Combine all factors multiplicatively
    probability = (
        base
        * distance_mod
        * contest_penalty
        * fatigue_mod
        * cas_bonus
        * dribble_mod
        * streak_mod
        * rim_mod
        * hz_bonus
        * corner_bonus
        * clutch_mod
        * volume_bonus
    )

    return clamp(probability, 0.02, 0.98)
