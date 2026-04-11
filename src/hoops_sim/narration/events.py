"""Rich narration event types for broadcast-quality play-by-play.

Typed event classes for every micro-action the simulator computes.
These replace the flat SimEvent with structured data that the narration
layer can use to compose multi-sentence possession narratives.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


class NarrationEventType(enum.Enum):
    """All event types the narration pipeline handles."""

    POSSESSION_START = "possession_start"
    BALL_ADVANCE = "ball_advance"
    DRIBBLE_MOVE = "dribble_move"
    SCREEN_ACTION = "screen_action"
    PASS_ACTION = "pass_action"
    DRIVE = "drive"
    SHOT_ATTEMPT = "shot_attempt"
    SHOT_RESULT = "shot_result"
    REBOUND = "rebound"
    TURNOVER = "turnover"
    FOUL = "foul"
    FREE_THROW = "free_throw"
    SUBSTITUTION = "substitution"
    TIMEOUT = "timeout"
    DEAD_BALL = "dead_ball"
    QUARTER_EVENT = "quarter_event"
    MOMENTUM = "momentum"
    MILESTONE = "milestone"
    BLOCK = "block"
    STEAL = "steal"
    OFF_BALL_ACTION = "off_ball_action"
    DEFENSIVE_ACTION = "defensive_action"
    # New event types for richer micro-action narration
    PROBING = "probing"
    SHOT_CLOCK_PRESSURE = "shot_clock_pressure"
    PLAY_CALL = "play_call"
    MISMATCH = "mismatch"
    CROWD_REACTION = "crowd_reaction"


class ShotResultType(enum.Enum):
    """How a shot resolved."""

    SWISH = "swish"
    RATTLE_IN = "rattle_in"
    BANKED_IN = "banked_in"
    RIM_OUT = "rim_out"
    AIRBALL = "airball"
    BLOCKED = "blocked"


class QuarterEventKind(enum.Enum):
    """Kind of quarter boundary event."""

    QUARTER_START = "quarter_start"
    QUARTER_END = "quarter_end"
    HALFTIME = "halftime"
    OVERTIME_START = "overtime_start"
    GAME_END = "game_end"


class DeadBallKind(enum.Enum):
    """Kind of dead ball situation."""

    FREE_THROW = "free_throw"
    INBOUND = "inbound"
    BETWEEN_POSSESSION = "between_possession"
    JUMP_BALL = "jump_ball"


class MomentumKind(enum.Enum):
    """Kind of momentum event."""

    RUN_STARTED = "run_started"
    RUN_EXTENDED = "run_extended"
    RUN_BROKEN = "run_broken"
    LEAD_CHANGE = "lead_change"
    TIE_GAME = "tie_game"


class OffBallActionKind(enum.Enum):
    """Kind of off-ball offensive action."""

    CUT = "cut"
    SPOT_UP = "spot_up"
    RELOCATE = "relocate"
    SET_SCREEN = "set_screen"


class DefensiveActionKind(enum.Enum):
    """Kind of defensive action."""

    CLOSEOUT = "closeout"
    HELP_ROTATION = "help_rotation"
    SWITCH = "switch"
    DENY = "deny"
    DROP_COVERAGE = "drop_coverage"
    HEDGE = "hedge"


@dataclass
class BaseNarrationEvent:
    """Base class for all narration events."""

    event_type: NarrationEventType
    game_clock: float = 0.0
    shot_clock: float = 0.0
    quarter: int = 1
    home_score: int = 0
    away_score: int = 0
    possession_id: int = 0
    # Spatial context fields (Phase 4)
    court_location: str = ""      # "left wing", "top of the key", etc.
    drive_direction: str = ""     # "left", "right", "baseline", "middle"
    distance_description: str = ""  # "from deep", "24 feet"


@dataclass
class PossessionStartEvent(BaseNarrationEvent):
    """Emitted when a new possession begins."""

    event_type: NarrationEventType = NarrationEventType.POSSESSION_START
    ball_handler_name: str = ""
    ball_handler_id: int = 0
    offensive_team: str = ""
    defensive_team: str = ""
    play_call: str = ""
    is_transition: bool = False
    lineup_description: str = ""


@dataclass
class BallAdvanceEvent(BaseNarrationEvent):
    """Emitted when ball is brought up court."""

    event_type: NarrationEventType = NarrationEventType.BALL_ADVANCE
    ball_handler_name: str = ""
    is_transition: bool = False
    is_after_timeout: bool = False
    is_after_made_basket: bool = False
    seconds_to_advance: float = 0.0


@dataclass
class DribbleMoveEvent(BaseNarrationEvent):
    """Emitted when a dribble move is executed."""

    event_type: NarrationEventType = NarrationEventType.DRIBBLE_MOVE
    player_name: str = ""
    player_id: int = 0
    move_type: str = ""
    success: bool = True
    separation_gained: float = 0.0
    ankle_breaker: bool = False
    defender_name: str = ""
    combo_count: int = 0
    turnover: bool = False


@dataclass
class ScreenEvent(BaseNarrationEvent):
    """Emitted when a screen action occurs."""

    event_type: NarrationEventType = NarrationEventType.SCREEN_ACTION
    screener_name: str = ""
    handler_name: str = ""
    screen_type: str = ""
    defender_reaction: str = ""
    pnr_coverage: str = ""
    roller_or_popper: str = ""
    switch_occurred: bool = False


@dataclass
class PassEvent(BaseNarrationEvent):
    """Emitted when a pass is made."""

    event_type: NarrationEventType = NarrationEventType.PASS_ACTION
    passer_name: str = ""
    passer_id: int = 0
    receiver_name: str = ""
    receiver_id: int = 0
    pass_type: str = ""
    distance: float = 0.0
    is_entry_pass: bool = False
    is_skip_pass: bool = False
    is_kick_out: bool = False
    lane_quality: float = 0.0


@dataclass
class DriveEvent(BaseNarrationEvent):
    """Emitted when a player drives to the basket."""

    event_type: NarrationEventType = NarrationEventType.DRIVE
    driver_name: str = ""
    driver_id: int = 0
    finish_type: str = ""
    help_defender_name: str = ""
    kick_out: bool = False
    kick_out_target: str = ""
    defender_name: str = ""
    distance_to_basket: float = 0.0


@dataclass
class ShotAttemptEvent(BaseNarrationEvent):
    """Emitted when a shot is attempted (before resolution)."""

    event_type: NarrationEventType = NarrationEventType.SHOT_ATTEMPT
    shooter_name: str = ""
    shooter_id: int = 0
    distance: float = 0.0
    zone: str = ""
    is_three: bool = False
    is_open: bool = False
    is_catch_and_shoot: bool = False
    is_off_dribble: bool = False
    contest_quality: float = 0.0
    defender_name: str = ""
    action_chain: List[str] = field(default_factory=list)


@dataclass
class ShotResultEvent(BaseNarrationEvent):
    """Emitted when a shot resolves."""

    event_type: NarrationEventType = NarrationEventType.SHOT_RESULT
    shooter_name: str = ""
    shooter_id: int = 0
    made: bool = False
    points: int = 0
    distance: float = 0.0
    zone: str = ""
    is_three: bool = False
    is_dunk: bool = False
    is_and_one: bool = False
    result_type: str = ""
    team_name: str = ""
    new_score_home: int = 0
    new_score_away: int = 0
    lead: int = 0
    # Context from the action chain
    action_chain: List[str] = field(default_factory=list)
    assist_player_name: str = ""
    finish_type: str = ""


@dataclass
class ReboundEvent(BaseNarrationEvent):
    """Emitted when a rebound is grabbed."""

    event_type: NarrationEventType = NarrationEventType.REBOUND
    rebounder_name: str = ""
    rebounder_id: int = 0
    is_offensive: bool = False
    is_contested: bool = False
    team_name: str = ""


@dataclass
class TurnoverEvent(BaseNarrationEvent):
    """Emitted on a turnover."""

    event_type: NarrationEventType = NarrationEventType.TURNOVER
    player_name: str = ""
    player_id: int = 0
    is_steal: bool = False
    stealer_name: str = ""
    stealer_id: int = 0
    turnover_type: str = ""
    team_name: str = ""


@dataclass
class BlockEvent(BaseNarrationEvent):
    """Emitted when a shot is blocked."""

    event_type: NarrationEventType = NarrationEventType.BLOCK
    blocker_name: str = ""
    blocker_id: int = 0
    shooter_name: str = ""
    shooter_id: int = 0


@dataclass
class FoulEvent(BaseNarrationEvent):
    """Emitted when a foul is called."""

    event_type: NarrationEventType = NarrationEventType.FOUL
    fouler_name: str = ""
    fouler_id: int = 0
    victim_name: str = ""
    victim_id: int = 0
    foul_type: str = "personal"
    team_fouls: int = 0
    personal_fouls: int = 0
    free_throws_awarded: int = 0
    is_in_bonus: bool = False
    is_foul_trouble: bool = False


@dataclass
class FreeThrowEvent(BaseNarrationEvent):
    """Emitted for each free throw attempt."""

    event_type: NarrationEventType = NarrationEventType.FREE_THROW
    shooter_name: str = ""
    shooter_id: int = 0
    made: bool = False
    attempt_number: int = 1
    total_attempts: int = 2


@dataclass
class SubstitutionEvent(BaseNarrationEvent):
    """Emitted when a substitution occurs."""

    event_type: NarrationEventType = NarrationEventType.SUBSTITUTION
    player_in_name: str = ""
    player_in_id: int = 0
    player_out_name: str = ""
    player_out_id: int = 0
    team_name: str = ""
    reason: str = ""
    lineup_description: str = ""


@dataclass
class TimeoutEvent(BaseNarrationEvent):
    """Emitted when a timeout is called."""

    event_type: NarrationEventType = NarrationEventType.TIMEOUT
    team_name: str = ""
    timeouts_remaining: int = 0
    opponent_run: int = 0
    score_diff: int = 0


@dataclass
class QuarterBoundaryEvent(BaseNarrationEvent):
    """Emitted at quarter boundaries."""

    event_type: NarrationEventType = NarrationEventType.QUARTER_EVENT
    kind: QuarterEventKind = QuarterEventKind.QUARTER_END
    home_team: str = ""
    away_team: str = ""


@dataclass
class MomentumEvent(BaseNarrationEvent):
    """Emitted when a momentum shift is detected."""

    event_type: NarrationEventType = NarrationEventType.MOMENTUM
    kind: MomentumKind = MomentumKind.RUN_STARTED
    team_name: str = ""
    run_points: int = 0
    run_possessions: int = 0


@dataclass
class MilestoneEvent(BaseNarrationEvent):
    """Emitted when a player reaches a scoring milestone."""

    event_type: NarrationEventType = NarrationEventType.MILESTONE
    player_name: str = ""
    player_id: int = 0
    milestone_type: str = ""
    value: int = 0
    description: str = ""


@dataclass
class OffBallEvent(BaseNarrationEvent):
    """Emitted for significant off-ball actions."""

    event_type: NarrationEventType = NarrationEventType.OFF_BALL_ACTION
    player_name: str = ""
    action_kind: OffBallActionKind = OffBallActionKind.CUT
    description: str = ""


@dataclass
class DefensiveEvent(BaseNarrationEvent):
    """Emitted for significant defensive actions."""

    event_type: NarrationEventType = NarrationEventType.DEFENSIVE_ACTION
    player_name: str = ""
    action_kind: DefensiveActionKind = DefensiveActionKind.CLOSEOUT
    description: str = ""


@dataclass
class ProbingEvent(BaseNarrationEvent):
    """Emitted when a ball handler is sizing up the defense."""

    event_type: NarrationEventType = NarrationEventType.PROBING
    player_name: str = ""
    player_id: int = 0
    defender_name: str = ""
    ticks_held: int = 0


@dataclass
class ShotClockPressureEvent(BaseNarrationEvent):
    """Emitted when the shot clock is low and creates urgency."""

    event_type: NarrationEventType = NarrationEventType.SHOT_CLOCK_PRESSURE
    team_name: str = ""
    handler_name: str = ""


@dataclass
class PlayCallEvent(BaseNarrationEvent):
    """Emitted when a play is called (screen, iso, etc.)."""

    event_type: NarrationEventType = NarrationEventType.PLAY_CALL
    caller_name: str = ""
    play_name: str = ""


@dataclass
class MismatchEvent(BaseNarrationEvent):
    """Emitted when a mismatch is detected after a switch."""

    event_type: NarrationEventType = NarrationEventType.MISMATCH
    offensive_player_name: str = ""
    defensive_player_name: str = ""
    mismatch_type: str = ""  # "size", "speed", "skill"


@dataclass
class CrowdReactionEvent(BaseNarrationEvent):
    """Emitted for crowd atmosphere narration."""

    event_type: NarrationEventType = NarrationEventType.CROWD_REACTION
    reaction_type: str = ""  # "erupts", "silenced", "building"
    is_home_positive: bool = True


# Union type for all narration events
from typing import Union

NarrationEventUnion = Union[
    PossessionStartEvent,
    BallAdvanceEvent,
    DribbleMoveEvent,
    ScreenEvent,
    PassEvent,
    DriveEvent,
    ShotAttemptEvent,
    ShotResultEvent,
    ReboundEvent,
    TurnoverEvent,
    BlockEvent,
    FoulEvent,
    FreeThrowEvent,
    SubstitutionEvent,
    TimeoutEvent,
    QuarterBoundaryEvent,
    MomentumEvent,
    MilestoneEvent,
    OffBallEvent,
    DefensiveEvent,
    ProbingEvent,
    ShotClockPressureEvent,
    PlayCallEvent,
    MismatchEvent,
    CrowdReactionEvent,
]
