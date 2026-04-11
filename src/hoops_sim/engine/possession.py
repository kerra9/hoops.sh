"""Possession state machine: all states from inbound through end."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class PossessionState(enum.Enum):
    """States a possession can be in."""

    PRE_INBOUND = "pre_inbound"  # Before the ball is inbounded
    INBOUND = "inbound"  # Ball is being inbounded
    LIVE = "live"  # Ball is live, offense executing
    SHOT_IN_AIR = "shot_in_air"  # Shot has been released
    FREE_THROW = "free_throw"  # Free throw being shot
    DEAD_BALL = "dead_ball"  # Whistle blown, play stopped
    TRANSITION = "transition"  # Fast break / transition offense
    REBOUND = "rebound"  # Shot missed, battle for rebound
    TURNOVER = "turnover"  # Ball turned over
    MADE_BASKET = "made_basket"  # Shot went in
    END_OF_QUARTER = "end_of_quarter"  # Quarter/period ended
    JUMP_BALL = "jump_ball"  # Jump ball situation
    TIMEOUT = "timeout"  # Timeout called


class PossessionResult(enum.Enum):
    """How a possession ended."""

    MADE_TWO = "made_two"
    MADE_THREE = "made_three"
    MADE_FREE_THROW = "made_free_throw"
    MISSED_SHOT = "missed_shot"
    TURNOVER = "turnover"
    END_OF_QUARTER = "end_of_quarter"
    OFFENSIVE_FOUL = "offensive_foul"
    SHOT_CLOCK_VIOLATION = "shot_clock_violation"


@dataclass
class PossessionTracker:
    """Tracks the current state of a possession.

    Manages transitions between possession states and records events.
    """

    state: PossessionState = PossessionState.PRE_INBOUND
    offensive_team_id: int = 0
    defensive_team_id: int = 0
    ball_handler_id: int | None = None
    possession_number: int = 0
    ticks_in_state: int = 0
    ticks_total: int = 0
    result: PossessionResult | None = None
    events: list[object] = field(default_factory=list)

    def transition_to(self, new_state: PossessionState) -> None:
        """Transition to a new possession state."""
        self.state = new_state
        self.ticks_in_state = 0

    def tick(self) -> None:
        """Advance the possession by one tick."""
        self.ticks_in_state += 1
        self.ticks_total += 1

    def new_possession(self, offensive_team_id: int, defensive_team_id: int) -> None:
        """Start a new possession."""
        self.offensive_team_id = offensive_team_id
        self.defensive_team_id = defensive_team_id
        self.ball_handler_id = None
        self.possession_number += 1
        self.ticks_total = 0
        self.ticks_in_state = 0
        self.result = None
        self.events = []
        self.state = PossessionState.PRE_INBOUND

    def end_possession(self, result: PossessionResult) -> None:
        """End the current possession with a result."""
        self.result = result
        self.state = PossessionState.DEAD_BALL

    def is_live(self) -> bool:
        """Check if the ball is live (clock running, play in progress)."""
        return self.state in (
            PossessionState.LIVE,
            PossessionState.TRANSITION,
            PossessionState.SHOT_IN_AIR,
            PossessionState.REBOUND,
        )

    def is_dead(self) -> bool:
        """Check if play is stopped."""
        return self.state in (
            PossessionState.DEAD_BALL,
            PossessionState.FREE_THROW,
            PossessionState.TIMEOUT,
            PossessionState.END_OF_QUARTER,
            PossessionState.PRE_INBOUND,
            PossessionState.JUMP_BALL,
        )

    def seconds_elapsed(self) -> float:
        """Seconds elapsed in this possession."""
        return self.ticks_total * 0.1
