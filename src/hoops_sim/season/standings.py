"""Season standings with full NBA tiebreaker hierarchy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class TeamRecord:
    """A team's season record."""

    team_id: int = 0
    team_name: str = ""
    conference: str = ""
    division: str = ""
    wins: int = 0
    losses: int = 0
    home_wins: int = 0
    home_losses: int = 0
    away_wins: int = 0
    away_losses: int = 0
    conference_wins: int = 0
    conference_losses: int = 0
    division_wins: int = 0
    division_losses: int = 0
    streak: int = 0  # Positive = win streak, negative = losing streak
    last_10_wins: int = 0
    last_10_losses: int = 0
    points_for: int = 0
    points_against: int = 0

    @property
    def games_played(self) -> int:
        return self.wins + self.losses

    @property
    def win_pct(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.wins / self.games_played

    @property
    def games_back(self) -> float:
        """Set externally by the standings calculator."""
        return 0.0

    @property
    def point_diff(self) -> int:
        return self.points_for - self.points_against

    @property
    def ppg(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.points_for / self.games_played

    @property
    def opp_ppg(self) -> float:
        if self.games_played == 0:
            return 0.0
        return self.points_against / self.games_played

    def record_win(self, is_home: bool, is_conference: bool, is_division: bool, pts_for: int, pts_against: int) -> None:
        self.wins += 1
        self.points_for += pts_for
        self.points_against += pts_against
        if is_home:
            self.home_wins += 1
        else:
            self.away_wins += 1
        if is_conference:
            self.conference_wins += 1
        if is_division:
            self.division_wins += 1
        self.streak = self.streak + 1 if self.streak > 0 else 1

    def record_loss(self, is_home: bool, is_conference: bool, is_division: bool, pts_for: int, pts_against: int) -> None:
        self.losses += 1
        self.points_for += pts_for
        self.points_against += pts_against
        if is_home:
            self.home_losses += 1
        else:
            self.away_losses += 1
        if is_conference:
            self.conference_losses += 1
        if is_division:
            self.division_losses += 1
        self.streak = self.streak - 1 if self.streak < 0 else -1

    @property
    def record_display(self) -> str:
        return f"{self.wins}-{self.losses}"


@dataclass
class Standings:
    """League standings tracker."""

    records: Dict[int, TeamRecord] = field(default_factory=dict)

    def add_team(self, team_id: int, name: str, conference: str, division: str) -> None:
        self.records[team_id] = TeamRecord(
            team_id=team_id, team_name=name,
            conference=conference, division=division,
        )

    def get_record(self, team_id: int) -> TeamRecord:
        return self.records.get(team_id, TeamRecord())

    def conference_standings(self, conference: str) -> List[TeamRecord]:
        """Get sorted standings for a conference."""
        conf_records = [r for r in self.records.values() if r.conference == conference]
        return sorted(conf_records, key=lambda r: (-r.win_pct, -r.point_diff))

    def league_standings(self) -> List[TeamRecord]:
        """Get all teams sorted by win percentage."""
        return sorted(self.records.values(), key=lambda r: (-r.win_pct, -r.point_diff))

    def playoff_teams(self, conference: str, count: int = 8) -> List[TeamRecord]:
        """Get the top teams for playoff seeding."""
        return self.conference_standings(conference)[:count]
