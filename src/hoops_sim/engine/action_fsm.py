"""Per-player micro-action state machine for tick-driven simulation.

Every on-court player gets an ActionStateMachine that tracks what they are
doing right now, how long it takes, and what happens when it finishes.
The FSM is the bridge between the AI layer (which decides *what* to do)
and the physics layer (which moves bodies around the court).
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Union

from hoops_sim.physics.vec import Vec2


# ---------------------------------------------------------------------------
# Micro-action enums
# ---------------------------------------------------------------------------

class BallHandlerState(enum.Enum):
    """States for the player who has the ball."""

    BRINGING_BALL_UP = "bringing_ball_up"
    CALLING_PLAY = "calling_play"
    DRIBBLING_IN_PLACE = "dribbling_in_place"
    EXECUTING_DRIBBLE_MOVE = "executing_dribble_move"
    USING_SCREEN = "using_screen"
    DRIVING = "driving"
    PULLING_UP = "pulling_up"
    PASSING = "passing"
    POSTING_UP = "posting_up"
    TRIPLE_THREAT = "triple_threat"
    FINISHING = "finishing"


class OffBallOffenseState(enum.Enum):
    """States for offensive players without the ball."""

    SETTING_SCREEN = "setting_screen"
    ROLLING = "rolling"
    POPPING = "popping"
    CUTTING = "cutting"
    SPOTTING_UP = "spotting_up"
    CRASHING_BOARDS = "crashing_boards"
    RECEIVING_PASS = "receiving_pass"
    RELOCATING = "relocating"
    STANDING = "standing"


class DefenderState(enum.Enum):
    """States for defensive players."""

    GUARDING_ON_BALL = "guarding_on_ball"
    DENYING_PASS = "denying_pass"
    HELPING = "helping"
    RECOVERING = "recovering"
    CLOSING_OUT = "closing_out"
    SWITCHING = "switching"
    HEDGING = "hedging"
    CONTESTING_SHOT = "contesting_shot"
    BOXING_OUT = "boxing_out"
    TAGGING_ROLLER = "tagging_roller"
    GETTING_BACK = "getting_back"


# Union type for all micro-action states
MicroAction = Union[BallHandlerState, OffBallOffenseState, DefenderState]


class MovementIntent(enum.Enum):
    """How urgently the player is moving."""

    STAND = "stand"
    WALK = "walk"
    JOG = "jog"
    SPRINT = "sprint"
    LATERAL = "lateral"
    BACKPEDAL = "backpedal"


# ---------------------------------------------------------------------------
# Duration ranges for each action (in ticks, where 1 tick = 0.1s)
# ---------------------------------------------------------------------------

# (min_ticks, max_ticks) for each micro-action
ACTION_DURATIONS: dict[MicroAction, tuple[int, int]] = {
    # Ball handler states
    BallHandlerState.BRINGING_BALL_UP: (30, 60),
    BallHandlerState.CALLING_PLAY: (5, 10),
    BallHandlerState.DRIBBLING_IN_PLACE: (3, 20),
    BallHandlerState.EXECUTING_DRIBBLE_MOVE: (3, 6),
    BallHandlerState.USING_SCREEN: (5, 10),
    BallHandlerState.DRIVING: (5, 20),
    BallHandlerState.PULLING_UP: (3, 5),
    BallHandlerState.PASSING: (3, 8),
    BallHandlerState.POSTING_UP: (10, 40),
    BallHandlerState.TRIPLE_THREAT: (5, 20),
    BallHandlerState.FINISHING: (3, 8),
    # Off-ball offense states
    OffBallOffenseState.SETTING_SCREEN: (5, 10),
    OffBallOffenseState.ROLLING: (5, 15),
    OffBallOffenseState.POPPING: (5, 15),
    OffBallOffenseState.CUTTING: (5, 15),
    OffBallOffenseState.SPOTTING_UP: (10, 50),
    OffBallOffenseState.CRASHING_BOARDS: (5, 15),
    OffBallOffenseState.RECEIVING_PASS: (3, 5),
    OffBallOffenseState.RELOCATING: (5, 20),
    OffBallOffenseState.STANDING: (5, 30),
    # Defender states
    DefenderState.GUARDING_ON_BALL: (1, 100),
    DefenderState.DENYING_PASS: (5, 50),
    DefenderState.HELPING: (3, 10),
    DefenderState.RECOVERING: (5, 15),
    DefenderState.CLOSING_OUT: (3, 8),
    DefenderState.SWITCHING: (1, 3),
    DefenderState.HEDGING: (5, 10),
    DefenderState.CONTESTING_SHOT: (3, 5),
    DefenderState.BOXING_OUT: (5, 10),
    DefenderState.TAGGING_ROLLER: (3, 10),
    DefenderState.GETTING_BACK: (10, 30),
}


# Which states can be interrupted by a new decision
INTERRUPTIBLE_STATES: set[MicroAction] = {
    BallHandlerState.DRIBBLING_IN_PLACE,
    BallHandlerState.TRIPLE_THREAT,
    OffBallOffenseState.SPOTTING_UP,
    OffBallOffenseState.STANDING,
    OffBallOffenseState.RELOCATING,
    DefenderState.GUARDING_ON_BALL,
    DefenderState.DENYING_PASS,
}


# ---------------------------------------------------------------------------
# The state machine itself
# ---------------------------------------------------------------------------

@dataclass
class ActionStateMachine:
    """Per-player micro-action state machine.

    Each on-court player gets one of these. It tracks their current action,
    where they are trying to go, and how much time is left on the action.
    """

    current_state: MicroAction = OffBallOffenseState.STANDING
    ticks_remaining: int = 0
    movement_target: Vec2 = field(default_factory=lambda: Vec2(0.0, 0.0))
    movement_intent: MovementIntent = MovementIntent.STAND
    interruptible: bool = True

    # Context data for the current action
    context: dict[str, Any] = field(default_factory=dict)

    # Combo tracking for dribble moves
    combo_count: int = 0
    last_dribble_success: bool = False

    # Separation from defender (feet) -- capped at 5.0, decays 0.5/second
    defender_separation: float = 3.0
    # Maximum separation (feet)
    MAX_SEPARATION: float = 5.0
    # Separation decay per tick (0.5 ft/sec * 0.1 sec/tick = 0.05 ft/tick)
    SEPARATION_DECAY_PER_TICK: float = 0.05
    # Maximum dribble moves per action chain (4 for ball_handle > 90)
    MAX_DRIBBLE_MOVES: int = 3

    # Whether this player is on offense
    is_offense: bool = True

    def transition_to(
        self,
        new_state: MicroAction,
        ticks: int,
        target: Vec2 | None = None,
        intent: MovementIntent = MovementIntent.JOG,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Transition to a new micro-action state."""
        self.current_state = new_state
        self.ticks_remaining = max(1, ticks)
        if target is not None:
            self.movement_target = target
        self.movement_intent = intent
        self.interruptible = new_state in INTERRUPTIBLE_STATES
        self.context = context or {}

    def tick(self) -> bool:
        """Advance the FSM by one tick.

        Returns True if the action just completed (ticks hit 0).
        Also applies separation decay each tick.
        """
        if self.ticks_remaining > 0:
            self.ticks_remaining -= 1

        # Separation decay: 0.5 feet/sec = 0.05 feet/tick at 0.1s/tick
        if self.defender_separation > 0.0:
            self.defender_separation = max(
                0.0, self.defender_separation - self.SEPARATION_DECAY_PER_TICK,
            )

        return self.ticks_remaining == 0

    @property
    def is_complete(self) -> bool:
        """Whether the current action has finished."""
        return self.ticks_remaining <= 0

    @property
    def can_interrupt(self) -> bool:
        """Whether the current action can be interrupted by a new decision."""
        return self.interruptible or self.is_complete

    @property
    def is_ball_handler_state(self) -> bool:
        return isinstance(self.current_state, BallHandlerState)

    @property
    def is_offense_state(self) -> bool:
        return isinstance(self.current_state, (BallHandlerState, OffBallOffenseState))

    @property
    def is_defense_state(self) -> bool:
        return isinstance(self.current_state, DefenderState)

    def reset_combo(self) -> None:
        """Reset the dribble combo counter."""
        self.combo_count = 0
        self.last_dribble_success = False

    def increment_combo(self, success: bool) -> None:
        """Track a dribble move in a combo chain."""
        if success:
            self.combo_count += 1
            self.last_dribble_success = True
        else:
            self.reset_combo()

    def add_separation(self, amount: float) -> None:
        """Add separation from a dribble move, capped at MAX_SEPARATION."""
        self.defender_separation = min(
            self.MAX_SEPARATION,
            self.defender_separation + amount,
        )

    @property
    def can_dribble(self) -> bool:
        """Whether the player can execute another dribble move (cap check)."""
        return self.combo_count < self.MAX_DRIBBLE_MOVES

    def set_dribble_cap(self, ball_handle: int) -> None:
        """Set the dribble move cap based on ball handling rating.

        Elite handlers (90+) get 4 moves; everyone else gets 3.
        """
        self.MAX_DRIBBLE_MOVES = 4 if ball_handle > 90 else 3


# ---------------------------------------------------------------------------
# Possession-level event types emitted by the micro-action loop
# ---------------------------------------------------------------------------

class PossessionEventType(enum.Enum):
    """Events that can end or alter a possession during micro-action processing."""

    SHOT_ATTEMPTED = "shot_attempted"
    PASS_COMPLETED = "pass_completed"
    PASS_INTERCEPTED = "pass_intercepted"
    TURNOVER = "turnover"
    FOUL_CALLED = "foul_called"
    SHOT_CLOCK_VIOLATION = "shot_clock_violation"
    QUARTER_END = "quarter_end"
    DRIBBLE_MOVE_SUCCESS = "dribble_move_success"
    DRIBBLE_MOVE_FAIL = "dribble_move_fail"
    ANKLE_BREAKER = "ankle_breaker"
    SCREEN_SET = "screen_set"
    BLOCK = "block"
    STEAL = "steal"
    AND_ONE = "and_one"
    MADE_BASKET = "made_basket"
    MISSED_SHOT = "missed_shot"
    OFFENSIVE_REBOUND = "offensive_rebound"
    DEFENSIVE_REBOUND = "defensive_rebound"


@dataclass
class PossessionEvent:
    """An event that occurred during a tick of possession simulation."""

    event_type: PossessionEventType
    player_id: int | None = None
    secondary_player_id: int | None = None
    description: str = ""
    data: dict[str, Any] = field(default_factory=dict)
