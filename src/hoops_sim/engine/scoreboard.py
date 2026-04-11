"""Scoreboard service: single source of truth for all scoring actions.

Consolidates the copy-pasted scoring logic that was spread across
_execute_shot, _execute_drive, _execute_post_up, _free_throws,
_turnover, _steal, _foul_on_drive, and _resolve_rebound into one
class with clear methods for each stat-changing event.
"""

from __future__ import annotations

from typing import Optional

from hoops_sim.engine.game import GameState
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.psychology.confidence import ConfidenceTracker
from hoops_sim.psychology.momentum import MomentumTracker

# Optional import: LiveStatTracker is no longer a hard dependency.
# The scoreboard can operate without it (decoupled architecture).
try:
    from hoops_sim.narration.stat_tracker import LiveStatTracker as _LiveStatTracker
except ImportError:
    _LiveStatTracker = None  # type: ignore[assignment,misc]


class Scoreboard:
    """Central service for recording all scoring and stat events.

    Every basket, miss, turnover, steal, foul, and rebound flows
    through here. No other code should directly mutate score or
    player/team stats.
    """

    def __init__(
        self,
        game_state: GameState,
        home_stats: TeamGameStats,
        away_stats: TeamGameStats,
        confidence: ConfidenceTracker,
        momentum: MomentumTracker,
        broadcast_stats: Optional[LiveStatTracker] = None,
    ) -> None:
        self.gs = game_state
        self.home_stats = home_stats
        self.away_stats = away_stats
        self.confidence = confidence
        self.momentum = momentum
        self.broadcast_stats = broadcast_stats

    # -- Scoring helpers ------------------------------------------------------

    def _team_stats(self, is_home: bool) -> TeamGameStats:
        return self.home_stats if is_home else self.away_stats

    def _player_stats(self, player_id: int, is_home: bool):
        return self._team_stats(is_home).get_player(player_id)

    # -- Made baskets ---------------------------------------------------------

    def record_basket(
        self,
        player_id: int,
        player_name: str,
        is_home: bool,
        points: int,
        is_three: bool,
        is_paint: bool = False,
        assister_id: Optional[int] = None,
        assister_name: Optional[str] = None,
        is_dunk: bool = False,
    ) -> None:
        """Record a made basket and update every subsystem."""
        stats = self._player_stats(player_id, is_home)
        quarter = self.gs.clock.quarter

        # Player stats
        if points == 1:
            # Free throw path -- use record_made_ft
            stats.record_made_ft()
        else:
            stats.record_made_shot(is_three=is_three)

        # Game score
        self.gs.score.add_points(is_home, points, quarter)

        # Team stats
        team_stats = self._team_stats(is_home)
        team_stats.points += points
        if is_paint and points > 1:
            team_stats.points_in_paint += points

        # Confidence
        if points > 1:
            self.confidence.on_made_shot(player_id, was_three=is_three)

        # Momentum
        if is_home:
            self.momentum.on_home_score(points)
        else:
            self.momentum.on_away_score(points)

        if is_dunk:
            self.momentum.on_dunk(is_home)

        # Assist credit
        if assister_id and assister_id != player_id:
            a_stats = self._player_stats(assister_id, is_home)
            a_stats.assists += 1
            self.confidence.on_assist(assister_id)
            if self.broadcast_stats and assister_name:
                self.broadcast_stats.on_assist(assister_id, assister_name)

        # Broadcast stat tracker
        if self.broadcast_stats:
            self.broadcast_stats.on_made_shot(
                player_id, player_name, is_home,
                points, is_three, self.gs.clock.game_clock,
            )

    # -- Missed shots ---------------------------------------------------------

    def record_miss(
        self,
        player_id: int,
        player_name: str,
        is_home: bool,
        is_three: bool,
    ) -> None:
        """Record a missed field goal."""
        stats = self._player_stats(player_id, is_home)
        stats.record_missed_shot(is_three=is_three)
        self.confidence.on_missed_shot(player_id)
        if self.broadcast_stats:
            self.broadcast_stats.on_missed_shot(
                player_id, player_name, is_home, is_three,
            )

    def record_missed_ft(
        self,
        player_id: int,
        is_home: bool,
    ) -> None:
        """Record a missed free throw."""
        stats = self._player_stats(player_id, is_home)
        stats.record_missed_ft()

    # -- Turnovers and steals -------------------------------------------------

    def record_turnover(
        self,
        player_id: int,
        player_name: str,
        is_home: bool,
    ) -> None:
        """Record a non-steal turnover."""
        stats = self._player_stats(player_id, is_home)
        stats.turnovers += 1
        self._team_stats(is_home).turnovers += 1
        self.confidence.on_turnover(player_id)
        self.momentum.on_turnover(is_home)
        if self.broadcast_stats:
            self.broadcast_stats.on_turnover(player_id, player_name)

    def record_steal(
        self,
        handler_id: int,
        handler_name: str,
        handler_is_home: bool,
        stealer_id: int,
        stealer_name: str,
    ) -> None:
        """Record a steal (turnover for handler, steal for defender)."""
        # Turnover side
        h_stats = self._player_stats(handler_id, handler_is_home)
        h_stats.turnovers += 1
        self._team_stats(handler_is_home).turnovers += 1
        self.confidence.on_turnover(handler_id)

        # Steal side
        s_stats = self._player_stats(stealer_id, not handler_is_home)
        s_stats.steals += 1
        self.momentum.on_steal(not handler_is_home)
        if self.broadcast_stats:
            self.broadcast_stats.on_steal(stealer_id, stealer_name)
            self.broadcast_stats.on_turnover(handler_id, handler_name)

    # -- Fouls ----------------------------------------------------------------

    def record_foul(
        self,
        fouler_id: int,
        fouler_name: str,
        fouler_is_home: bool,
        fouler_personal_fouls: int,
    ) -> None:
        """Record a personal foul."""
        d_stats = self._player_stats(fouler_id, fouler_is_home)
        d_stats.personal_fouls += 1
        if fouler_is_home:
            self.gs.home_team_fouls += 1
        else:
            self.gs.away_team_fouls += 1
        if self.broadcast_stats:
            self.broadcast_stats.on_foul(fouler_id, fouler_name)

    # -- Rebounds -------------------------------------------------------------

    def record_rebound(
        self,
        player_id: int,
        player_name: str,
        is_home: bool,
        is_offensive: bool,
    ) -> None:
        """Record a rebound."""
        stats = self._player_stats(player_id, is_home)
        if is_offensive:
            stats.offensive_rebounds += 1
        else:
            stats.defensive_rebounds += 1
        if self.broadcast_stats:
            self.broadcast_stats.on_rebound(player_id, player_name, is_offensive)

    # -- Blocks ---------------------------------------------------------------

    def record_block(
        self,
        blocker_id: int,
        blocker_name: str,
        blocker_is_home: bool,
    ) -> None:
        """Record a blocked shot."""
        stats = self._player_stats(blocker_id, blocker_is_home)
        stats.blocks += 1
        if self.broadcast_stats:
            self.broadcast_stats.on_block(blocker_id, blocker_name)

    # -- Shot clock violation -------------------------------------------------

    def record_shot_clock_violation(self, is_home: bool) -> None:
        """Record a shot clock violation (team turnover)."""
        self._team_stats(is_home).turnovers += 1
