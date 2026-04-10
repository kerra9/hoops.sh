"""Defensive scheme system: man-to-man, zones, and tactical adjustments.

The coach selects a defensive scheme and can adjust mid-game.
Each scheme modifies how defenders position themselves and contest shots.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


class DefensiveScheme(enum.Enum):
    """Available defensive schemes."""

    MAN_TO_MAN = "man_to_man"
    ZONE_2_3 = "zone_2_3"
    ZONE_3_2 = "zone_3_2"
    ZONE_1_3_1 = "zone_1_3_1"
    SWITCH_EVERYTHING = "switch_everything"
    DROP_COVERAGE = "drop_coverage"  # Big drops back on PnR
    HEDGE_AND_RECOVER = "hedge_and_recover"  # Big jumps out on PnR
    FULL_COURT_PRESS = "full_court_press"


@dataclass(frozen=True)
class SchemeModifiers:
    """How a defensive scheme modifies game outcomes."""

    # Contest quality modifier (higher = better contest)
    perimeter_contest: float = 1.0
    interior_contest: float = 1.0

    # Turnover generation modifier
    steal_chance_mod: float = 1.0

    # Rebound positioning modifier
    defensive_rebound_mod: float = 1.0

    # Energy cost modifier (zones are less tiring)
    energy_cost_mod: float = 1.0

    # Vulnerability: what this scheme is weak against
    three_point_vulnerability: float = 1.0  # >1 = gives up more threes
    paint_vulnerability: float = 1.0  # >1 = gives up more paint points
    transition_vulnerability: float = 1.0  # >1 = worse in transition

    # Fast break chance after defensive stop
    fast_break_chance: float = 0.15


SCHEME_MODIFIERS: dict[DefensiveScheme, SchemeModifiers] = {
    DefensiveScheme.MAN_TO_MAN: SchemeModifiers(
        perimeter_contest=1.0,
        interior_contest=1.0,
        steal_chance_mod=1.0,
        defensive_rebound_mod=1.0,
        energy_cost_mod=1.0,
        three_point_vulnerability=1.0,
        paint_vulnerability=1.0,
        fast_break_chance=0.15,
    ),
    DefensiveScheme.ZONE_2_3: SchemeModifiers(
        perimeter_contest=0.85,  # Weaker on perimeter
        interior_contest=1.15,  # Stronger inside
        steal_chance_mod=0.9,
        defensive_rebound_mod=1.1,  # Better box-out positioning
        energy_cost_mod=0.85,  # Less tiring
        three_point_vulnerability=1.2,  # Gives up open threes
        paint_vulnerability=0.75,  # Strong in the paint
        fast_break_chance=0.10,
    ),
    DefensiveScheme.ZONE_3_2: SchemeModifiers(
        perimeter_contest=1.05,  # Better on perimeter
        interior_contest=0.90,  # Weaker inside
        steal_chance_mod=1.05,
        defensive_rebound_mod=0.95,
        energy_cost_mod=0.85,
        three_point_vulnerability=0.9,
        paint_vulnerability=1.15,
        fast_break_chance=0.10,
    ),
    DefensiveScheme.ZONE_1_3_1: SchemeModifiers(
        perimeter_contest=0.95,
        interior_contest=1.0,
        steal_chance_mod=1.15,  # Trapping zone creates turnovers
        defensive_rebound_mod=0.90,
        energy_cost_mod=0.90,
        three_point_vulnerability=1.1,
        paint_vulnerability=1.1,  # Vulnerable on baseline
        fast_break_chance=0.18,  # Steals lead to fast breaks
    ),
    DefensiveScheme.SWITCH_EVERYTHING: SchemeModifiers(
        perimeter_contest=1.1,
        interior_contest=0.85,  # Mismatches in the post
        steal_chance_mod=0.95,
        defensive_rebound_mod=0.95,
        energy_cost_mod=1.1,  # Tiring to switch constantly
        three_point_vulnerability=0.9,
        paint_vulnerability=1.15,  # Size mismatches
        fast_break_chance=0.15,
    ),
    DefensiveScheme.DROP_COVERAGE: SchemeModifiers(
        perimeter_contest=0.80,  # Big is back, guard fights over screen
        interior_contest=1.2,  # Big is protecting the rim
        steal_chance_mod=0.85,
        defensive_rebound_mod=1.1,
        energy_cost_mod=0.90,
        three_point_vulnerability=1.25,  # Mid-range / pull-up threes open
        paint_vulnerability=0.70,  # Excellent rim protection
        fast_break_chance=0.12,
    ),
    DefensiveScheme.HEDGE_AND_RECOVER: SchemeModifiers(
        perimeter_contest=1.15,  # Big jumps out to contest
        interior_contest=0.85,  # Roller is briefly open
        steal_chance_mod=1.05,
        defensive_rebound_mod=0.90,
        energy_cost_mod=1.15,  # Very tiring for the big
        three_point_vulnerability=0.85,
        paint_vulnerability=1.10,  # Roll man can be open
        fast_break_chance=0.15,
    ),
    DefensiveScheme.FULL_COURT_PRESS: SchemeModifiers(
        perimeter_contest=1.1,
        interior_contest=0.85,
        steal_chance_mod=1.4,  # High steal rate
        defensive_rebound_mod=0.85,
        energy_cost_mod=1.4,  # Extremely tiring
        three_point_vulnerability=1.1,
        paint_vulnerability=1.2,  # Easy baskets if broken
        transition_vulnerability=1.3,
        fast_break_chance=0.25,
    ),
}


def get_scheme_modifiers(scheme: DefensiveScheme) -> SchemeModifiers:
    """Get the modifiers for a defensive scheme."""
    return SCHEME_MODIFIERS.get(scheme, SCHEME_MODIFIERS[DefensiveScheme.MAN_TO_MAN])


def select_defensive_scheme(
    opponent_three_pct: float,
    opponent_paint_points_pct: float,
    own_team_athleticism: float,
    score_diff: int,
    quarter: int,
    minutes_remaining: float,
) -> DefensiveScheme:
    """AI-driven defensive scheme selection.

    Args:
        opponent_three_pct: Opponent 3PT% this game (0-1).
        opponent_paint_points_pct: Fraction of opponent points in the paint.
        own_team_athleticism: Average athleticism of own team (0-99).
        score_diff: Score difference (positive = leading).
        quarter: Current quarter.
        minutes_remaining: Minutes left in the quarter.

    Returns:
        Recommended defensive scheme.
    """
    # If opponent is shooting well from three, go to a 3-2 zone
    if opponent_three_pct > 0.40:
        return DefensiveScheme.ZONE_3_2

    # If opponent is dominating the paint, use 2-3 zone
    if opponent_paint_points_pct > 0.55:
        return DefensiveScheme.ZONE_2_3

    # If we're down big, press to create turnovers
    if score_diff < -15 and quarter >= 3:
        return DefensiveScheme.FULL_COURT_PRESS

    # Clutch time with a lead: switch everything to prevent easy buckets
    if quarter >= 4 and minutes_remaining < 3.0 and score_diff > 0:
        return DefensiveScheme.SWITCH_EVERYTHING

    # Athletic teams can hedge and recover
    if own_team_athleticism > 70:
        return DefensiveScheme.HEDGE_AND_RECOVER

    # Default: man-to-man
    return DefensiveScheme.MAN_TO_MAN
