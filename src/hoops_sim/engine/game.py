"""Game orchestrator: manages the overall flow of a basketball game."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from hoops_sim.engine.clock import GameClock
from hoops_sim.engine.possession import PossessionResult, PossessionState, PossessionTracker
from hoops_sim.models.team import Team
from hoops_sim.utils.constants import TICK_DURATION


class GamePhase(enum.Enum):
    """High-level game phase."""

    PRE_GAME = "pre_game"
    QUARTER = "quarter"
    QUARTER_BREAK = "quarter_break"
    HALFTIME = "halftime"
    OVERTIME = "overtime"
    POST_GAME = "post_game"


@dataclass
class GameScore:
    """Score tracker."""

    home: int = 0
    away: int = 0
    quarter_scores_home: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    quarter_scores_away: List[int] = field(default_factory=lambda: [0, 0, 0, 0])

    @property
    def diff(self) -> int:
        """Score difference (positive = home leads)."""
        return self.home - self.away

    def add_points(self, is_home: bool, points: int, quarter: int) -> None:
        """Add points to the score."""
        if is_home:
            self.home += points
        else:
            self.away += points

        # Extend quarter scores if needed (overtime)
        while quarter > len(self.quarter_scores_home):
            self.quarter_scores_home.append(0)
            self.quarter_scores_away.append(0)

        idx = quarter - 1
        if is_home:
            self.quarter_scores_home[idx] += points
        else:
            self.quarter_scores_away[idx] += points


@dataclass
class GameState:
    """Complete state of a basketball game at any point in time.

    This is the central data structure that all systems read from
    and write to during simulation.
    """

    # Teams
    home_team: Optional[Team] = None
    away_team: Optional[Team] = None

    # Game flow
    phase: GamePhase = GamePhase.PRE_GAME
    clock: GameClock = field(default_factory=GameClock)
    possession: PossessionTracker = field(default_factory=PossessionTracker)
    score: GameScore = field(default_factory=GameScore)

    # Timeouts remaining
    home_timeouts: int = 7
    away_timeouts: int = 7

    # Team fouls per quarter
    home_team_fouls: int = 0
    away_team_fouls: int = 0

    # Game stats
    total_possessions: int = 0

    def is_home_on_offense(self) -> bool:
        """Check if the home team has the ball."""
        if self.home_team is None:
            return False
        return self.possession.offensive_team_id == self.home_team.id

    def is_in_bonus(self, team_on_offense: bool) -> bool:
        """Check if the defending team is in the bonus (5+ fouls).

        Args:
            team_on_offense: True if checking for the offensive team's benefit.
        """
        if team_on_offense:
            # Defending team's fouls matter
            fouls = self.away_team_fouls if self.is_home_on_offense() else self.home_team_fouls
        else:
            fouls = self.home_team_fouls if self.is_home_on_offense() else self.away_team_fouls
        return fouls >= 5

    def start_quarter(self, quarter: int) -> None:
        """Initialize a new quarter."""
        self.clock.start_quarter(quarter)
        self.phase = GamePhase.QUARTER if quarter <= 4 else GamePhase.OVERTIME
        self.home_team_fouls = 0
        self.away_team_fouls = 0

    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.phase == GamePhase.POST_GAME

    def is_tied(self) -> bool:
        return self.score.home == self.score.away

    def leading_team_id(self) -> Optional[int]:
        """Get the ID of the leading team, or None if tied."""
        if self.score.home > self.score.away:
            return self.home_team.id if self.home_team else None
        if self.score.away > self.score.home:
            return self.away_team.id if self.away_team else None
        return None
