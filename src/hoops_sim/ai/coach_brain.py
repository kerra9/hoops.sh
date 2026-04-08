"""Coach AI: rotation management, timeout decisions, and in-game adjustments."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import List, Optional


class CoachDecision(enum.Enum):
    """Types of coaching decisions."""

    NO_ACTION = "no_action"
    CALL_TIMEOUT = "call_timeout"
    MAKE_SUBSTITUTION = "make_substitution"
    CHANGE_DEFENSE = "change_defense"
    CHANGE_OFFENSE = "change_offense"
    DOUBLE_TEAM = "double_team"
    REDUCE_USAGE = "reduce_usage"


@dataclass
class SubstitutionPlan:
    """A planned substitution."""

    player_out_id: int
    player_in_id: int
    reason: str = ""


@dataclass
class CoachAction:
    """An action decided by the coach AI."""

    decision: CoachDecision
    substitution: Optional[SubstitutionPlan] = None
    target_player_id: Optional[int] = None
    detail: str = ""


def should_call_timeout(
    opponent_run: int,
    own_turnovers_last_3: int,
    timeouts_remaining: int,
    is_clutch: bool,
    quarter: int,
) -> bool:
    """Decide whether to call a timeout.

    Args:
        opponent_run: Points scored by opponent in their current run.
        own_turnovers_last_3: Turnovers in the last 3 possessions.
        timeouts_remaining: How many timeouts are left.
        is_clutch: Whether it's clutch time.
        quarter: Current quarter number.

    Returns:
        True if a timeout should be called.
    """
    if timeouts_remaining <= 0:
        return False

    # Save timeouts for clutch time
    if quarter < 4 and timeouts_remaining <= 2:
        return False

    # Call timeout on big runs
    if opponent_run >= 10:
        return True
    if opponent_run >= 7 and own_turnovers_last_3 >= 2:
        return True

    return False


def evaluate_substitution_need(
    player_energy_pct: float,
    player_fouls: int,
    minutes_played: float,
    quarter: int,
    is_starter: bool,
    is_closing_lineup: bool,
) -> float:
    """Evaluate how urgently a player needs to be substituted.

    Returns:
        Urgency score (0-1). Higher = more urgently needs a sub.
    """
    urgency = 0.0

    # Fatigue
    if player_energy_pct < 0.3:
        urgency += 0.5
    elif player_energy_pct < 0.5:
        urgency += 0.3
    elif player_energy_pct < 0.7:
        urgency += 0.1

    # Foul trouble
    if player_fouls >= 5:
        urgency += 0.7  # About to foul out
    elif player_fouls >= 4 and quarter < 4:
        urgency += 0.4  # Save for later
    elif player_fouls >= 3 and quarter <= 2:
        urgency += 0.2

    # Minutes management
    if minutes_played > 38:
        urgency += 0.3
    elif minutes_played > 32:
        urgency += 0.1

    # Don't sub closing lineup players
    if is_closing_lineup and quarter >= 4:
        urgency *= 0.3

    return min(1.0, urgency)


def between_possession_adjustment(
    opponent_consecutive_scores: int,
    opponent_hot_player_points: int,
    own_cold_player_fg_pct: float,
    own_cold_player_attempts: int,
    personality: str,
) -> CoachAction:
    """Make micro-adjustments between possessions.

    Args:
        opponent_consecutive_scores: How many in a row the opponent scored.
        opponent_hot_player_points: Points by opponent's hottest player recently.
        own_cold_player_fg_pct: FG% of own coldest player recently.
        own_cold_player_attempts: Attempts by own coldest player.
        personality: Coach personality type.

    Returns:
        CoachAction with the adjustment.
    """
    # Opponent on a run -- consider double team or defensive change
    if opponent_hot_player_points >= 8:
        if personality == "aggressive":
            return CoachAction(
                decision=CoachDecision.DOUBLE_TEAM,
                detail="Double-teaming opponent hot player",
            )
        return CoachAction(
            decision=CoachDecision.CHANGE_DEFENSE,
            detail="Switching defensive scheme to contain hot player",
        )

    # Own player is cold -- reduce their usage
    if own_cold_player_fg_pct <= 0.15 and own_cold_player_attempts >= 4:
        return CoachAction(
            decision=CoachDecision.REDUCE_USAGE,
            detail="Reducing usage of cold player",
        )

    return CoachAction(decision=CoachDecision.NO_ACTION)
