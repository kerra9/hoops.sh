"""Pick-and-roll coverage types and configuration."""

from __future__ import annotations

import enum
from dataclasses import dataclass


class PnRCoverageType(enum.Enum):
    """8 types of pick-and-roll defensive coverage."""

    DROP = "drop"  # Big drops back, gives up mid-range
    SWITCH = "switch"  # Switch all screens
    ICE = "ice"  # Force ball handler baseline, away from screen
    BLITZ = "blitz"  # Both defenders trap the ball handler
    HEDGE = "hedge"  # Big steps out briefly then recovers
    SHOW = "show"  # Big shows hard, doesn't fully commit
    VEER = "veer"  # Guard goes under the screen
    TRAP = "trap"  # Full trap with rotation behind


@dataclass
class PnRCoverageConfig:
    """Configuration for how a team defends pick-and-rolls."""

    primary_coverage: PnRCoverageType = PnRCoverageType.DROP
    vs_elite_handler: PnRCoverageType = PnRCoverageType.BLITZ
    vs_non_shooter_roller: PnRCoverageType = PnRCoverageType.DROP
    vs_shooting_roller: PnRCoverageType = PnRCoverageType.SWITCH
    switch_threshold: int = 70  # Min perimeter defense for big to switch


@dataclass
class PnRCoverageResult:
    """Result of PnR coverage evaluation."""

    coverage_used: PnRCoverageType
    ball_handler_open: bool  # Did the handler get free?
    roller_open: bool  # Did the roller get free?
    mid_range_open: bool  # Is the mid-range available?
    three_open: bool  # Is a kick-out three available?
    mismatch_created: bool  # Did a switch create a mismatch?


def evaluate_pnr_coverage(
    coverage: PnRCoverageType,
    handler_ball_handle: int,
    handler_three_point: int,
    screener_roll_rating: int,
    screener_can_shoot: bool,
    defender_lateral: int,
    big_defender_perimeter: int,
) -> PnRCoverageResult:
    """Evaluate the outcome of a PnR coverage type.

    Args:
        coverage: The defensive coverage being used.
        handler_ball_handle: Ball handler's handle rating.
        handler_three_point: Ball handler's 3PT rating.
        screener_roll_rating: Screener's finishing/roll quality.
        screener_can_shoot: Whether the screener can pop for a jumper.
        defender_lateral: On-ball defender's lateral quickness.
        big_defender_perimeter: Big defender's perimeter defense.

    Returns:
        PnRCoverageResult showing what opportunities are created.
    """
    result = PnRCoverageResult(
        coverage_used=coverage,
        ball_handler_open=False,
        roller_open=False,
        mid_range_open=False,
        three_open=False,
        mismatch_created=False,
    )

    if coverage == PnRCoverageType.DROP:
        # Big drops back: mid-range is open, roller is contested
        result.mid_range_open = True
        result.roller_open = False
        # Elite handlers can pull up
        if handler_ball_handle > 80:
            result.ball_handler_open = True

    elif coverage == PnRCoverageType.SWITCH:
        # Switch creates potential mismatch
        if big_defender_perimeter < 60 and handler_ball_handle > 75:
            result.mismatch_created = True
            result.ball_handler_open = True
        if screener_roll_rating > 70:
            result.roller_open = True  # Smaller defender on screener

    elif coverage == PnRCoverageType.ICE:
        # Force baseline: takes away the screen direction
        # Good vs non-shooting handlers
        if handler_three_point > 80:
            result.three_open = True  # Handler can pull up from other side
        result.mid_range_open = False

    elif coverage == PnRCoverageType.BLITZ:
        # Trap the handler: roller is wide open, kick-out three available
        result.roller_open = True
        result.three_open = True
        # Elite handlers can split the trap
        if handler_ball_handle > 88:
            result.ball_handler_open = True

    elif coverage == PnRCoverageType.HEDGE:
        # Big steps out then recovers
        if handler_ball_handle > 82:
            result.ball_handler_open = True  # Can beat the recovery
        if screener_roll_rating > 75:
            result.roller_open = True  # Roll while big recovers

    elif coverage == PnRCoverageType.SHOW:
        result.mid_range_open = True
        if screener_can_shoot:
            result.three_open = True  # Pop for three

    elif coverage == PnRCoverageType.VEER:
        # Guard goes under: open three for handler
        if handler_three_point > 70:
            result.three_open = True
            result.ball_handler_open = True

    elif coverage == PnRCoverageType.TRAP:
        result.roller_open = True
        result.three_open = True

    return result
