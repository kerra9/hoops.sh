"""Game event dataclasses: the contract between simulation and narration.

These are pure data structures with no logic beyond validation.
The simulation layer builds them; the broadcast layer reads them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class PlayerRef:
    """Lightweight player reference for event data."""

    id: int
    name: str
    team: str
    jersey: int = 0
    nickname: str = ""
    signature_move: str = ""


@dataclass
class ClockSnapshot:
    """Clock state at the moment of a possession."""

    quarter: int = 1
    game_clock: float = 720.0
    shot_clock: float = 24.0
    is_clutch: bool = False
    is_end_of_quarter: bool = False
    time_description: str = ""

    def __post_init__(self) -> None:
        if not self.time_description:
            self.time_description = _describe_time(
                self.quarter, self.game_clock,
            )


def _describe_time(quarter: int, game_clock: float) -> str:
    """Generate a human-readable time description."""
    if game_clock <= 120:
        return "under 2 minutes"
    if game_clock <= 300:
        return "under 5 minutes"
    if game_clock <= 420:
        return "midway through"
    return "early in the quarter"


@dataclass
class ScoreSnapshot:
    """Score state before and after a possession."""

    home_team: str = ""
    away_team: str = ""
    home_score: int = 0
    away_score: int = 0
    home_score_after: int = 0
    away_score_after: int = 0

    @property
    def lead_team(self) -> str:
        if self.home_score_after > self.away_score_after:
            return self.home_team
        if self.away_score_after > self.home_score_after:
            return self.away_team
        return ""

    @property
    def margin(self) -> int:
        return abs(self.home_score_after - self.away_score_after)

    @property
    def margin_before(self) -> int:
        return abs(self.home_score - self.away_score)

    @property
    def is_tie(self) -> bool:
        return self.home_score_after == self.away_score_after

    @property
    def lead_changed(self) -> bool:
        before_leader = (
            "home" if self.home_score > self.away_score
            else "away" if self.away_score > self.home_score
            else "tie"
        )
        after_leader = (
            "home" if self.home_score_after > self.away_score_after
            else "away" if self.away_score_after > self.home_score_after
            else "tie"
        )
        return before_leader != after_leader


@dataclass
class MomentumSnapshot:
    """Momentum state at the time of a possession."""

    home_momentum: float = 0.0
    away_momentum: float = 0.0
    scoring_run: int = 0
    run_team: str = ""
    is_momentum_shift: bool = False


@dataclass
class MoveResult:
    """Result of a single dribble move within an action chain."""

    move_type: str = ""  # "crossover", "hesitation", etc.
    success: bool = True
    defender_reaction: str = ""  # "bites", "stays_home", "recovers", "falls"
    separation_gained: float = 0.0


@dataclass
class ActionChainResult:
    """Result of 1-3 dribble moves as a coherent unit."""

    player: Optional[PlayerRef] = None
    defender: Optional[PlayerRef] = None
    moves: List[MoveResult] = field(default_factory=list)
    total_separation: float = 0.0
    outcome: str = ""  # "separation", "no_advantage", "turnover", "ankle_breaker"


@dataclass
class ScreenResult:
    """Result of a screen action."""

    screener: Optional[PlayerRef] = None
    ball_handler: Optional[PlayerRef] = None
    defender: Optional[PlayerRef] = None
    screen_type: str = ""  # "ball_screen", "off_ball", "pin_down"
    effective: bool = False
    defender_got_screened: bool = False
    switch_occurred: bool = False
    new_defender: Optional[PlayerRef] = None


@dataclass
class PassResult:
    """Result of a pass action."""

    passer: Optional[PlayerRef] = None
    receiver: Optional[PlayerRef] = None
    pass_type: str = ""  # "entry", "kick", "lob", "skip", "swing"
    successful: bool = True
    is_hockey_assist: bool = False


@dataclass
class DriveResult:
    """Result of a drive to the basket."""

    driver: Optional[PlayerRef] = None
    defender: Optional[PlayerRef] = None
    direction: str = ""  # "left", "right", "baseline", "middle"
    got_to_rim: bool = False
    drew_help: bool = False
    help_defender: Optional[PlayerRef] = None
    finish_type: str = ""  # "layup", "floater", "dunk", "kick_out"


@dataclass
class ShotResult:
    """Result of a shot attempt."""

    shooter: Optional[PlayerRef] = None
    defender: Optional[PlayerRef] = None
    made: bool = False
    points: int = 0
    distance: float = 0.0
    zone: str = ""
    shot_type: str = ""  # "pull_up_three", "driving_layup", "dunk", etc.
    contest_level: str = ""  # "wide_open", "open", "contested", "heavily_contested"
    is_dunk: bool = False
    is_and_one: bool = False
    assister: Optional[PlayerRef] = None
    finish_type: str = ""  # "finger_roll", "reverse_layup", "poster", etc.
    shot_result_type: str = ""  # "swish", "rattle_in", "banked_in", "rim_out", "airball"


@dataclass
class TurnoverResult:
    """Result of a turnover."""

    player: Optional[PlayerRef] = None
    turnover_type: str = ""  # "steal", "bad_pass", "travel", "out_of_bounds", "offensive_foul"
    stealer: Optional[PlayerRef] = None
    description: str = ""


@dataclass
class FoulResult:
    """Result of a foul call."""

    fouler: Optional[PlayerRef] = None
    fouled_player: Optional[PlayerRef] = None
    foul_type: str = ""  # "shooting", "loose_ball", "flagrant", "offensive"
    free_throws_awarded: int = 0
    free_throws_made: int = 0
    fouler_foul_count: int = 0
    is_foul_trouble: bool = False  # 3rd before half, 4th, 5th


@dataclass
class ViolationResult:
    """Result of a violation."""

    violation_type: str = ""  # "shot_clock", "backcourt", "3_seconds", "out_of_bounds"
    player: Optional[PlayerRef] = None
    description: str = ""


@dataclass
class ReboundResult:
    """Result of a rebound after a missed shot."""

    rebounder: Optional[PlayerRef] = None
    is_offensive: bool = False
    is_putback: bool = False
    contested: bool = False


@dataclass
class PossessionResult:
    """Complete result of one possession -- the ONLY thing narration receives.

    The simulation builds this incrementally. Narration consumes it as a unit.
    Exactly ONE terminal event must be set (shot, turnover, foul, or violation).
    """

    # Who
    ball_handler: Optional[PlayerRef] = None
    primary_defender: Optional[PlayerRef] = None
    offensive_team: str = ""
    defensive_team: str = ""

    # What happened (setup)
    action_chain: Optional[ActionChainResult] = None
    screen: Optional[ScreenResult] = None
    passes: List[PassResult] = field(default_factory=list)
    drive: Optional[DriveResult] = None

    # How it ended (exactly ONE of these is set)
    shot: Optional[ShotResult] = None
    turnover: Optional[TurnoverResult] = None
    foul: Optional[FoulResult] = None
    violation: Optional[ViolationResult] = None

    # Context
    clock: ClockSnapshot = field(default_factory=ClockSnapshot)
    score: ScoreSnapshot = field(default_factory=ScoreSnapshot)
    momentum: MomentumSnapshot = field(default_factory=MomentumSnapshot)
    rebound: Optional[ReboundResult] = None

    # Metadata
    possession_number: int = 0
    is_transition: bool = False
    play_type: str = ""  # "pick_and_roll", "isolation", etc.

    def validate(self) -> None:
        """Assert exactly one terminal event is set.

        Raises ValueError if zero or more than one terminal events exist.
        """
        terminals = [
            self.shot is not None,
            self.turnover is not None,
            self.foul is not None,
            self.violation is not None,
        ]
        count = sum(terminals)
        if count == 0:
            raise ValueError("PossessionResult has no terminal event")
        if count > 1:
            set_names = []
            if self.shot is not None:
                set_names.append("shot")
            if self.turnover is not None:
                set_names.append("turnover")
            if self.foul is not None:
                set_names.append("foul")
            if self.violation is not None:
                set_names.append("violation")
            raise ValueError(
                f"PossessionResult has {count} terminal events: {set_names}"
            )

    @property
    def terminal_type(self) -> str:
        """Return which terminal event is set."""
        if self.shot is not None:
            return "shot"
        if self.turnover is not None:
            return "turnover"
        if self.foul is not None:
            return "foul"
        if self.violation is not None:
            return "violation"
        return "none"

    @property
    def scored(self) -> bool:
        """Whether this possession resulted in points."""
        if self.shot and self.shot.made:
            return True
        if self.foul and self.foul.free_throws_made > 0:
            return True
        return False

    @property
    def points_scored(self) -> int:
        """How many points were scored on this possession."""
        if self.shot and self.shot.made:
            return self.shot.points
        if self.foul:
            return self.foul.free_throws_made
        return 0
