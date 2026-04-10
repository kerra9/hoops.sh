"""Playoff bracket system: seeding, 7-game series, and bracket advancement.

After the 82-game regular season, the top 8 teams per conference
enter a 4-round playoff tournament with 7-game series.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class PlayoffRound(enum.Enum):
    """Playoff rounds."""

    FIRST_ROUND = "First Round"
    CONFERENCE_SEMIS = "Conference Semifinals"
    CONFERENCE_FINALS = "Conference Finals"
    NBA_FINALS = "NBA Finals"


ROUND_ORDER = [
    PlayoffRound.FIRST_ROUND,
    PlayoffRound.CONFERENCE_SEMIS,
    PlayoffRound.CONFERENCE_FINALS,
    PlayoffRound.NBA_FINALS,
]


@dataclass
class SeriesResult:
    """Result of a single game in a playoff series."""

    game_number: int
    home_team_id: int
    away_team_id: int
    home_score: int = 0
    away_score: int = 0
    played: bool = False

    @property
    def winner_id(self) -> int | None:
        if not self.played:
            return None
        return self.home_team_id if self.home_score > self.away_score else self.away_team_id


@dataclass
class PlayoffSeries:
    """A best-of-7 playoff series between two teams."""

    series_id: int
    round: PlayoffRound
    conference: str  # "East", "West", or "Finals"
    higher_seed_id: int
    lower_seed_id: int
    higher_seed_name: str = ""
    lower_seed_name: str = ""
    higher_seed_num: int = 1
    lower_seed_num: int = 8

    games: list[SeriesResult] = field(default_factory=list)
    higher_seed_wins: int = 0
    lower_seed_wins: int = 0

    def __post_init__(self) -> None:
        if not self.games:
            # NBA home court: 2-2-1-1-1 format
            # Higher seed gets games 1,2,5,7 at home
            home_pattern = [
                self.higher_seed_id,  # Game 1
                self.higher_seed_id,  # Game 2
                self.lower_seed_id,   # Game 3
                self.lower_seed_id,   # Game 4
                self.higher_seed_id,  # Game 5
                self.lower_seed_id,   # Game 6
                self.higher_seed_id,  # Game 7
            ]
            for i in range(7):
                home = home_pattern[i]
                away = self.lower_seed_id if home == self.higher_seed_id else self.higher_seed_id
                self.games.append(SeriesResult(
                    game_number=i + 1, home_team_id=home, away_team_id=away,
                ))

    @property
    def is_over(self) -> bool:
        return self.higher_seed_wins >= 4 or self.lower_seed_wins >= 4

    @property
    def winner_id(self) -> int | None:
        if self.higher_seed_wins >= 4:
            return self.higher_seed_id
        if self.lower_seed_wins >= 4:
            return self.lower_seed_id
        return None

    @property
    def loser_id(self) -> int | None:
        w = self.winner_id
        if w is None:
            return None
        return self.lower_seed_id if w == self.higher_seed_id else self.higher_seed_id

    @property
    def games_played(self) -> int:
        return sum(1 for g in self.games if g.played)

    @property
    def series_score(self) -> str:
        """e.g., 'BOS 3, LAL 2'."""
        h_name = self.higher_seed_name or str(self.higher_seed_id)
        l_name = self.lower_seed_name or str(self.lower_seed_id)
        return f"{h_name} {self.higher_seed_wins}, {l_name} {self.lower_seed_wins}"

    def next_game(self) -> SeriesResult | None:
        """Get the next unplayed game, or None if series is over."""
        if self.is_over:
            return None
        for g in self.games:
            if not g.played:
                return g
        return None

    def record_game(self, game_number: int, home_score: int, away_score: int) -> None:
        """Record the result of a game."""
        for g in self.games:
            if g.game_number == game_number and not g.played:
                g.home_score = home_score
                g.away_score = away_score
                g.played = True
                winner = g.winner_id
                if winner == self.higher_seed_id:
                    self.higher_seed_wins += 1
                elif winner == self.lower_seed_id:
                    self.lower_seed_wins += 1
                break


@dataclass
class PlayoffBracket:
    """Complete playoff bracket for both conferences."""

    season_year: int = 2025
    series: list[PlayoffSeries] = field(default_factory=list)
    champion_id: int | None = None
    finals_mvp_id: int | None = None

    def get_series_for_round(self, round: PlayoffRound) -> list[PlayoffSeries]:
        """Get all series in a given round."""
        return [s for s in self.series if s.round == round]

    def get_series_for_team(self, team_id: int) -> list[PlayoffSeries]:
        """Get all series involving a team."""
        return [
            s for s in self.series
            if s.higher_seed_id == team_id or s.lower_seed_id == team_id
        ]

    def current_round(self) -> PlayoffRound | None:
        """Get the current active round."""
        for round in ROUND_ORDER:
            round_series = self.get_series_for_round(round)
            if round_series and not all(s.is_over for s in round_series):
                return round
        return None

    def is_complete(self) -> bool:
        """Check if the entire playoffs are complete."""
        finals = self.get_series_for_round(PlayoffRound.NBA_FINALS)
        return bool(finals) and all(s.is_over for s in finals)

    def advance_round(self) -> bool:
        """Set up the next round of the playoffs.

        Returns True if a new round was created, False if playoffs are over.
        """
        # Find the latest completed round that doesn't have a next round yet
        for i, round in enumerate(ROUND_ORDER):
            existing = self.get_series_for_round(round)
            if existing and all(s.is_over for s in existing):
                # This round is complete; check if next round exists
                if i + 1 < len(ROUND_ORDER):
                    next_round = ROUND_ORDER[i + 1]
                    if not self.get_series_for_round(next_round):
                        return self._create_next_round(round, next_round)
        return False

    def _create_next_round(
        self, prev_round: PlayoffRound, next_round: PlayoffRound,
    ) -> bool:
        """Create next round matchups from previous round winners."""
        prev_series = self.get_series_for_round(prev_round)
        if not all(s.is_over for s in prev_series):
            return False

        if next_round == PlayoffRound.NBA_FINALS:
            # Finals: East champion vs West champion
            east_series = [s for s in prev_series if s.conference == "East"]
            west_series = [s for s in prev_series if s.conference == "West"]
            if east_series and west_series:
                east_champ_id = east_series[0].winner_id
                west_champ_id = west_series[0].winner_id
                if east_champ_id is not None and west_champ_id is not None:
                    # Higher seed by regular season record (simplified: use seed numbers)
                    self.series.append(PlayoffSeries(
                        series_id=len(self.series) + 1,
                        round=PlayoffRound.NBA_FINALS,
                        conference="Finals",
                        higher_seed_id=east_champ_id,
                        lower_seed_id=west_champ_id,
                        higher_seed_name=east_series[0].higher_seed_name
                        if east_series[0].winner_id == east_series[0].higher_seed_id
                        else east_series[0].lower_seed_name,
                        lower_seed_name=west_series[0].higher_seed_name
                        if west_series[0].winner_id == west_series[0].higher_seed_id
                        else west_series[0].lower_seed_name,
                        higher_seed_num=1,
                        lower_seed_num=1,
                    ))
                    return True
            return False

        # Conference rounds: pair winners by seed
        for conf in ["East", "West"]:
            conf_series = [s for s in prev_series if s.conference == conf]
            winners = []
            for s in conf_series:
                w = s.winner_id
                if w is not None:
                    # Carry forward seed info
                    if w == s.higher_seed_id:
                        winners.append((w, s.higher_seed_num, s.higher_seed_name))
                    else:
                        winners.append((w, s.lower_seed_num, s.lower_seed_name))

            # Sort by seed number (lower = higher seed)
            winners.sort(key=lambda x: x[1])

            # Pair: best vs worst remaining
            for i in range(len(winners) // 2):
                high = winners[i]
                low = winners[-(i + 1)]
                self.series.append(PlayoffSeries(
                    series_id=len(self.series) + 1,
                    round=next_round,
                    conference=conf,
                    higher_seed_id=high[0],
                    lower_seed_id=low[0],
                    higher_seed_name=high[2],
                    lower_seed_name=low[2],
                    higher_seed_num=high[1],
                    lower_seed_num=low[1],
                ))

        return True


def create_playoff_bracket(
    east_seeds: list[tuple[int, str]],
    west_seeds: list[tuple[int, str]],
    season_year: int = 2025,
) -> PlayoffBracket:
    """Create a playoff bracket from conference seedings.

    Args:
        east_seeds: List of (team_id, team_name) for top 8 East teams, in seed order.
        west_seeds: List of (team_id, team_name) for top 8 West teams, in seed order.
        season_year: The season year.

    Returns:
        PlayoffBracket with first-round matchups created.
    """
    bracket = PlayoffBracket(season_year=season_year)

    # First round matchups: 1v8, 2v7, 3v6, 4v5
    matchups = [(0, 7), (1, 6), (2, 5), (3, 4)]

    for conf_name, seeds in [("East", east_seeds), ("West", west_seeds)]:
        for high_idx, low_idx in matchups:
            if high_idx < len(seeds) and low_idx < len(seeds):
                high_id, high_name = seeds[high_idx]
                low_id, low_name = seeds[low_idx]
                bracket.series.append(PlayoffSeries(
                    series_id=len(bracket.series) + 1,
                    round=PlayoffRound.FIRST_ROUND,
                    conference=conf_name,
                    higher_seed_id=high_id,
                    lower_seed_id=low_id,
                    higher_seed_name=high_name,
                    lower_seed_name=low_name,
                    higher_seed_num=high_idx + 1,
                    lower_seed_num=low_idx + 1,
                ))

    return bracket
