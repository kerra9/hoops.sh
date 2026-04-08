"""Season schedule generation and management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from hoops_sim.utils.rng import SeededRNG


@dataclass
class ScheduledGame:
    """A single scheduled game."""

    game_id: int = 0
    home_team_id: int = 0
    away_team_id: int = 0
    day: int = 0  # Day of the season (1-indexed)
    played: bool = False
    home_score: int = 0
    away_score: int = 0
    winner_id: Optional[int] = None

    def record_result(self, home_score: int, away_score: int) -> None:
        self.played = True
        self.home_score = home_score
        self.away_score = away_score
        self.winner_id = self.home_team_id if home_score > away_score else self.away_team_id


@dataclass
class SeasonSchedule:
    """Full season schedule."""

    games: List[ScheduledGame] = field(default_factory=list)
    total_days: int = 180  # ~6 months

    def games_on_day(self, day: int) -> List[ScheduledGame]:
        return [g for g in self.games if g.day == day]

    def team_games(self, team_id: int) -> List[ScheduledGame]:
        return [g for g in self.games if g.home_team_id == team_id or g.away_team_id == team_id]

    def next_unplayed(self, team_id: int) -> Optional[ScheduledGame]:
        for g in self.team_games(team_id):
            if not g.played:
                return g
        return None

    def games_remaining(self, team_id: int) -> int:
        return sum(1 for g in self.team_games(team_id) if not g.played)

    def games_played_count(self, team_id: int) -> int:
        return sum(1 for g in self.team_games(team_id) if g.played)


def generate_schedule(
    team_ids: List[int],
    games_per_team: int = 82,
    rng: Optional[SeededRNG] = None,
) -> SeasonSchedule:
    """Generate a simplified season schedule.

    Creates a round-robin schedule where each team plays the specified
    number of games, roughly evenly split between home and away.

    Args:
        team_ids: List of team IDs.
        games_per_team: Number of games each team plays.
        rng: Random number generator for scheduling randomness.

    Returns:
        A SeasonSchedule with all games.
    """
    if rng is None:
        rng = SeededRNG(seed=42)

    n = len(team_ids)
    if n < 2:
        return SeasonSchedule()

    games: List[ScheduledGame] = []
    game_id = 0

    # Generate round-robin matchups
    matchups: List[Tuple[int, int]] = []
    for i in range(n):
        for j in range(i + 1, n):
            # Each pair plays multiple times
            games_between = max(2, games_per_team * 2 // (n - 1))
            for k in range(games_between):
                if k % 2 == 0:
                    matchups.append((team_ids[i], team_ids[j]))
                else:
                    matchups.append((team_ids[j], team_ids[i]))

    # Shuffle and assign to days
    rng.shuffle(matchups)

    # Limit to the right number of games per team
    team_game_counts: Dict[int, int] = {tid: 0 for tid in team_ids}
    scheduled: List[Tuple[int, int]] = []

    for home, away in matchups:
        if team_game_counts[home] < games_per_team and team_game_counts[away] < games_per_team:
            scheduled.append((home, away))
            team_game_counts[home] += 1
            team_game_counts[away] += 1

    # Assign days
    games_per_day = max(1, n // 2)
    day = 1
    day_count = 0

    for home, away in scheduled:
        game_id += 1
        games.append(ScheduledGame(
            game_id=game_id,
            home_team_id=home,
            away_team_id=away,
            day=day,
        ))
        day_count += 1
        if day_count >= games_per_day:
            day += 1
            day_count = 0

    return SeasonSchedule(games=games, total_days=day)
