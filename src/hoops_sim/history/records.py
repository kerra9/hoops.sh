"""Game history and records tracking across seasons.

Stores game results, box scores, season averages, all-time records,
and franchise records. Supports Hall of Fame tracking for retired players.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GameRecord:
    """A single game result for the history books."""

    game_id: int = 0
    season_year: int = 2025
    day: int = 0
    is_playoff: bool = False

    home_team_id: int = 0
    away_team_id: int = 0
    home_team_name: str = ""
    away_team_name: str = ""
    home_score: int = 0
    away_score: int = 0

    # Notable performances
    top_scorer_name: str = ""
    top_scorer_points: int = 0

    @property
    def winner_id(self) -> int:
        return self.home_team_id if self.home_score > self.away_score else self.away_team_id

    @property
    def score_line(self) -> str:
        return f"{self.away_team_name} {self.away_score} @ {self.home_team_name} {self.home_score}"


@dataclass
class SeasonRecord:
    """A notable single-season record."""

    record_type: str  # "points", "rebounds", "assists", etc.
    value: float
    player_name: str
    team_name: str
    season_year: int


@dataclass
class FranchiseRecord:
    """Records for a single franchise."""

    team_id: int
    team_name: str
    all_time_wins: int = 0
    all_time_losses: int = 0
    championships: int = 0
    championship_years: list[int] = field(default_factory=list)
    best_season_wins: int = 0
    best_season_year: int = 0
    worst_season_wins: int = 82
    worst_season_year: int = 0

    # Single-game franchise records
    highest_score: int = 0
    highest_score_year: int = 0
    individual_high_points: int = 0
    individual_high_points_player: str = ""
    individual_high_points_year: int = 0


@dataclass
class HallOfFamer:
    """A Hall of Fame entry for a retired player."""

    player_name: str
    position: str
    career_ppg: float
    career_rpg: float
    career_apg: float
    seasons_played: int
    championships: int
    mvp_awards: int = 0
    all_star_selections: int = 0
    induction_year: int = 0


class HistoryTracker:
    """Tracks all historical data across seasons."""

    def __init__(self) -> None:
        self.game_history: list[GameRecord] = []
        self.season_records: list[SeasonRecord] = []
        self.franchise_records: dict[int, FranchiseRecord] = {}
        self.hall_of_fame: list[HallOfFamer] = []
        self._next_game_id = 1

    def record_game(
        self,
        season_year: int,
        day: int,
        home_team_id: int,
        away_team_id: int,
        home_team_name: str,
        away_team_name: str,
        home_score: int,
        away_score: int,
        top_scorer_name: str = "",
        top_scorer_points: int = 0,
        is_playoff: bool = False,
    ) -> GameRecord:
        """Record a completed game."""
        rec = GameRecord(
            game_id=self._next_game_id,
            season_year=season_year,
            day=day,
            is_playoff=is_playoff,
            home_team_id=home_team_id,
            away_team_id=away_team_id,
            home_team_name=home_team_name,
            away_team_name=away_team_name,
            home_score=home_score,
            away_score=away_score,
            top_scorer_name=top_scorer_name,
            top_scorer_points=top_scorer_points,
        )
        self._next_game_id += 1
        self.game_history.append(rec)

        # Update franchise records
        self._update_franchise_game(home_team_id, home_team_name, home_score, season_year)
        self._update_franchise_game(away_team_id, away_team_name, away_score, season_year)

        if top_scorer_points > 0:
            for tid, tname in [(home_team_id, home_team_name), (away_team_id, away_team_name)]:
                fr = self._ensure_franchise(tid, tname)
                if top_scorer_points > fr.individual_high_points:
                    fr.individual_high_points = top_scorer_points
                    fr.individual_high_points_player = top_scorer_name
                    fr.individual_high_points_year = season_year

        return rec

    def record_season_end(
        self,
        team_id: int,
        team_name: str,
        wins: int,
        losses: int,
        season_year: int,
        is_champion: bool = False,
    ) -> None:
        """Record end-of-season franchise data."""
        fr = self._ensure_franchise(team_id, team_name)
        fr.all_time_wins += wins
        fr.all_time_losses += losses

        if wins > fr.best_season_wins:
            fr.best_season_wins = wins
            fr.best_season_year = season_year
        if wins < fr.worst_season_wins:
            fr.worst_season_wins = wins
            fr.worst_season_year = season_year

        if is_champion:
            fr.championships += 1
            fr.championship_years.append(season_year)

    def check_season_record(
        self,
        record_type: str,
        value: float,
        player_name: str,
        team_name: str,
        season_year: int,
    ) -> bool:
        """Check if a value beats the existing season record.

        Returns True if it's a new record.
        """
        existing = [r for r in self.season_records if r.record_type == record_type]
        if not existing or value > existing[-1].value:
            self.season_records.append(SeasonRecord(
                record_type=record_type,
                value=value,
                player_name=player_name,
                team_name=team_name,
                season_year=season_year,
            ))
            # Keep sorted, only top record
            self.season_records = sorted(
                self.season_records, key=lambda r: (r.record_type, -r.value),
            )
            return True
        return False

    def games_for_season(self, season_year: int) -> list[GameRecord]:
        """Get all games for a specific season."""
        return [g for g in self.game_history if g.season_year == season_year]

    def games_for_team(self, team_id: int, season_year: int | None = None) -> list[GameRecord]:
        """Get all games involving a team."""
        games = [
            g for g in self.game_history
            if g.home_team_id == team_id or g.away_team_id == team_id
        ]
        if season_year is not None:
            games = [g for g in games if g.season_year == season_year]
        return games

    def _ensure_franchise(self, team_id: int, team_name: str) -> FranchiseRecord:
        if team_id not in self.franchise_records:
            self.franchise_records[team_id] = FranchiseRecord(
                team_id=team_id, team_name=team_name,
            )
        return self.franchise_records[team_id]

    def _update_franchise_game(
        self, team_id: int, team_name: str, score: int, season_year: int,
    ) -> None:
        fr = self._ensure_franchise(team_id, team_name)
        if score > fr.highest_score:
            fr.highest_score = score
            fr.highest_score_year = season_year
