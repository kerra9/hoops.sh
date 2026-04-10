"""Season-level statistics aggregation for players and teams.

Tracks per-player season averages (PPG, RPG, APG, FG%, etc.),
per-team season stats, and league leaders across stat categories.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.models.stats import PlayerGameStats, TeamGameStats


@dataclass
class PlayerSeasonStats:
    """Accumulated season stats for a single player."""

    player_id: int = 0
    player_name: str = ""
    team_id: int = 0
    games_played: int = 0

    # Totals
    total_points: int = 0
    total_fgm: int = 0
    total_fga: int = 0
    total_3pm: int = 0
    total_3pa: int = 0
    total_ftm: int = 0
    total_fta: int = 0
    total_oreb: int = 0
    total_dreb: int = 0
    total_assists: int = 0
    total_steals: int = 0
    total_blocks: int = 0
    total_turnovers: int = 0
    total_fouls: int = 0
    total_minutes: float = 0.0

    def add_game(self, gs: PlayerGameStats) -> None:
        """Accumulate stats from a single game."""
        self.games_played += 1
        self.total_points += gs.points
        self.total_fgm += gs.fgm
        self.total_fga += gs.fga
        self.total_3pm += gs.three_pm
        self.total_3pa += gs.three_pa
        self.total_ftm += gs.ftm
        self.total_fta += gs.fta
        self.total_oreb += gs.offensive_rebounds
        self.total_dreb += gs.defensive_rebounds
        self.total_assists += gs.assists
        self.total_steals += gs.steals
        self.total_blocks += gs.blocks
        self.total_turnovers += gs.turnovers
        self.total_fouls += gs.personal_fouls
        self.total_minutes += gs.minutes

    # -- Per-game averages ----------------------------------------------------

    @property
    def ppg(self) -> float:
        return self.total_points / self.games_played if self.games_played else 0.0

    @property
    def rpg(self) -> float:
        return (self.total_oreb + self.total_dreb) / self.games_played if self.games_played else 0.0

    @property
    def apg(self) -> float:
        return self.total_assists / self.games_played if self.games_played else 0.0

    @property
    def spg(self) -> float:
        return self.total_steals / self.games_played if self.games_played else 0.0

    @property
    def bpg(self) -> float:
        return self.total_blocks / self.games_played if self.games_played else 0.0

    @property
    def topg(self) -> float:
        return self.total_turnovers / self.games_played if self.games_played else 0.0

    @property
    def mpg(self) -> float:
        return self.total_minutes / self.games_played if self.games_played else 0.0

    @property
    def fg_pct(self) -> float:
        return self.total_fgm / self.total_fga if self.total_fga else 0.0

    @property
    def three_pct(self) -> float:
        return self.total_3pm / self.total_3pa if self.total_3pa else 0.0

    @property
    def ft_pct(self) -> float:
        return self.total_ftm / self.total_fta if self.total_fta else 0.0

    @property
    def total_rebounds(self) -> int:
        return self.total_oreb + self.total_dreb

    def stat_line(self) -> str:
        """Short stat line: '25.3 PPG, 7.2 RPG, 5.1 APG'."""
        parts = [f"{self.ppg:.1f} PPG"]
        if self.rpg >= 1.0:
            parts.append(f"{self.rpg:.1f} RPG")
        if self.apg >= 1.0:
            parts.append(f"{self.apg:.1f} APG")
        return ", ".join(parts)


@dataclass
class TeamSeasonStats:
    """Accumulated season stats for a team."""

    team_id: int = 0
    team_name: str = ""
    games_played: int = 0
    total_points_for: int = 0
    total_points_against: int = 0
    total_fgm: int = 0
    total_fga: int = 0
    total_turnovers: int = 0

    player_stats: dict[int, PlayerSeasonStats] = field(default_factory=dict)

    def add_game(self, team_stats: TeamGameStats, points_against: int) -> None:
        """Accumulate stats from a single game."""
        self.games_played += 1
        self.total_points_for += team_stats.points
        self.total_points_against += points_against
        fgm = sum(p.fgm for p in team_stats.player_stats.values())
        fga = sum(p.fga for p in team_stats.player_stats.values())
        self.total_fgm += fgm
        self.total_fga += fga
        self.total_turnovers += team_stats.turnovers

        for pid, pgs in team_stats.player_stats.items():
            if pgs.fga == 0 and pgs.points == 0 and pgs.rebounds == 0:
                continue  # Skip players who didn't play
            if pid not in self.player_stats:
                self.player_stats[pid] = PlayerSeasonStats(
                    player_id=pid,
                    player_name=pgs.player_name,
                    team_id=self.team_id,
                )
            self.player_stats[pid].add_game(pgs)

    @property
    def ppg(self) -> float:
        return self.total_points_for / self.games_played if self.games_played else 0.0

    @property
    def opp_ppg(self) -> float:
        return self.total_points_against / self.games_played if self.games_played else 0.0

    @property
    def point_diff(self) -> float:
        return self.ppg - self.opp_ppg

    @property
    def fg_pct(self) -> float:
        return self.total_fgm / self.total_fga if self.total_fga else 0.0


class SeasonStatsTracker:
    """Tracks season stats across all teams and players."""

    def __init__(self) -> None:
        self.team_stats: dict[int, TeamSeasonStats] = {}

    def ensure_team(self, team_id: int, team_name: str) -> TeamSeasonStats:
        if team_id not in self.team_stats:
            self.team_stats[team_id] = TeamSeasonStats(
                team_id=team_id, team_name=team_name,
            )
        return self.team_stats[team_id]

    def record_game(
        self,
        home_id: int,
        home_name: str,
        away_id: int,
        away_name: str,
        home_stats: TeamGameStats,
        away_stats: TeamGameStats,
    ) -> None:
        """Record a completed game into season stats."""
        h = self.ensure_team(home_id, home_name)
        a = self.ensure_team(away_id, away_name)
        h.add_game(home_stats, away_stats.points)
        a.add_game(away_stats, home_stats.points)

    def league_leaders(self, stat: str, top_n: int = 10) -> list[PlayerSeasonStats]:
        """Get top players in a stat category.

        stat: one of 'ppg', 'rpg', 'apg', 'spg', 'bpg', 'fg_pct', 'three_pct'
        """
        all_players: list[PlayerSeasonStats] = []
        for ts in self.team_stats.values():
            for ps in ts.player_stats.values():
                if ps.games_played >= 5:  # Minimum games qualifier
                    all_players.append(ps)

        if stat == "fg_pct":
            all_players = [p for p in all_players if p.total_fga >= 50]
        elif stat == "three_pct":
            all_players = [p for p in all_players if p.total_3pa >= 20]
        elif stat == "ft_pct":
            all_players = [p for p in all_players if p.total_fta >= 20]

        return sorted(all_players, key=lambda p: getattr(p, stat), reverse=True)[:top_n]
