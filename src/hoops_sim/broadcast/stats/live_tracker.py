"""Live stat tracker for the broadcast layer.

Independently tracks stats from the event stream for narration context.
Does NOT import from the simulation layer -- reads only from events.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from hoops_sim.events.game_events import PossessionResult


@dataclass
class PlayerBroadcastStats:
    """Stats tracked for broadcast purposes."""

    name: str = ""
    points: int = 0
    field_goals_made: int = 0
    field_goals_attempted: int = 0
    threes_made: int = 0
    threes_attempted: int = 0
    assists: int = 0
    rebounds: int = 0
    steals: int = 0
    blocks: int = 0
    turnovers: int = 0
    free_throws_made: int = 0
    free_throws_attempted: int = 0
    consecutive_makes: int = 0
    consecutive_misses: int = 0

    @property
    def fg_pct(self) -> float:
        if self.field_goals_attempted == 0:
            return 0.0
        return self.field_goals_made / self.field_goals_attempted

    @property
    def three_pct(self) -> float:
        if self.threes_attempted == 0:
            return 0.0
        return self.threes_made / self.threes_attempted

    @property
    def is_hot(self) -> bool:
        return self.consecutive_makes >= 3

    @property
    def is_cold(self) -> bool:
        return self.consecutive_misses >= 4


class BroadcastStatTracker:
    """Tracks player stats from the event stream for broadcast context.

    Consumes PossessionResult objects and maintains stats that the
    broadcast layer uses for stat weaving, milestone detection, etc.
    """

    def __init__(self, home_team: str = "", away_team: str = "") -> None:
        self.home_team = home_team
        self.away_team = away_team
        self._players: Dict[int, PlayerBroadcastStats] = {}
        self._team_points: Dict[str, int] = {home_team: 0, away_team: 0}

    def process_possession(self, p: PossessionResult) -> None:
        """Update stats from a possession result."""
        if p.shot:
            self._process_shot(p)
        if p.turnover:
            self._process_turnover(p)
        if p.foul:
            self._process_foul(p)
        if p.rebound:
            self._process_rebound(p)

    def _process_shot(self, p: PossessionResult) -> None:
        shot = p.shot
        if not shot or not shot.shooter:
            return

        stats = self._get_or_create(shot.shooter.id, shot.shooter.name)
        is_three = shot.points == 3

        if shot.made:
            stats.field_goals_made += 1
            stats.field_goals_attempted += 1
            stats.points += shot.points
            stats.consecutive_makes += 1
            stats.consecutive_misses = 0
            if is_three:
                stats.threes_made += 1
                stats.threes_attempted += 1
            # Update team points
            team = shot.shooter.team
            if team in self._team_points:
                self._team_points[team] += shot.points
        else:
            stats.field_goals_attempted += 1
            stats.consecutive_misses += 1
            stats.consecutive_makes = 0
            if is_three:
                stats.threes_attempted += 1

        # Assist tracking
        if shot.made and shot.assister:
            a_stats = self._get_or_create(shot.assister.id, shot.assister.name)
            a_stats.assists += 1

    def _process_turnover(self, p: PossessionResult) -> None:
        to = p.turnover
        if not to:
            return
        if to.player:
            stats = self._get_or_create(to.player.id, to.player.name)
            stats.turnovers += 1
        if to.stealer:
            s_stats = self._get_or_create(to.stealer.id, to.stealer.name)
            s_stats.steals += 1

    def _process_foul(self, p: PossessionResult) -> None:
        foul = p.foul
        if not foul:
            return
        if foul.free_throws_made > 0 and foul.fouled_player:
            stats = self._get_or_create(foul.fouled_player.id, foul.fouled_player.name)
            stats.free_throws_made += foul.free_throws_made
            stats.free_throws_attempted += foul.free_throws_awarded
            stats.points += foul.free_throws_made

    def _process_rebound(self, p: PossessionResult) -> None:
        reb = p.rebound
        if not reb or not reb.rebounder:
            return
        stats = self._get_or_create(reb.rebounder.id, reb.rebounder.name)
        stats.rebounds += 1

    def get_player_stats(self, player_id: int) -> PlayerBroadcastStats:
        """Get broadcast stats for a player."""
        return self._players.get(player_id, PlayerBroadcastStats())

    def get_team_points(self, team: str) -> int:
        return self._team_points.get(team, 0)

    def _get_or_create(self, player_id: int, name: str) -> PlayerBroadcastStats:
        if player_id not in self._players:
            self._players[player_id] = PlayerBroadcastStats(name=name)
        return self._players[player_id]
