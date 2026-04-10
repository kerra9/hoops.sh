"""Game context tracker for rich, situationally-aware narration.

Tracks scoring runs, player milestones, shooting streaks, matchup
history, and game situation to provide context for narration.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class ScoringRun:
    """Tracks a team's current scoring run."""

    team_name: str = ""
    points: int = 0
    possessions: int = 0

    def add_score(self, team: str, points: int) -> None:
        if team == self.team_name:
            self.points += points
            self.possessions += 1
        else:
            # Opponent scored, reset
            self.team_name = team
            self.points = points
            self.possessions = 1

    @property
    def is_significant(self) -> bool:
        return self.points >= 7


@dataclass
class PlayerGameContext:
    """Tracks a player's context for narration."""

    player_id: int
    player_name: str
    points: int = 0
    fg_made: int = 0
    fg_attempted: int = 0
    three_made: int = 0
    three_attempted: int = 0
    consecutive_makes: int = 0
    consecutive_misses: int = 0
    assists: int = 0
    announced_milestones: set = field(default_factory=set)

    def on_made_shot(self, points: int, is_three: bool) -> None:
        self.points += points
        self.fg_made += 1
        self.fg_attempted += 1
        self.consecutive_makes += 1
        self.consecutive_misses = 0
        if is_three:
            self.three_made += 1
            self.three_attempted += 1

    def on_missed_shot(self, is_three: bool) -> None:
        self.fg_attempted += 1
        self.consecutive_misses += 1
        self.consecutive_makes = 0
        if is_three:
            self.three_attempted += 1

    @property
    def is_hot(self) -> bool:
        return self.consecutive_makes >= 3

    @property
    def is_cold(self) -> bool:
        return self.consecutive_misses >= 4

    @property
    def next_milestone(self) -> int | None:
        """Next point milestone to announce (20, 30, 40, 50)."""
        for m in [20, 30, 40, 50]:
            if self.points >= m and m not in self.announced_milestones:
                return m
        return None


@dataclass
class GameNarrationContext:
    """Full game context for narration decisions."""

    scoring_run: ScoringRun = field(default_factory=ScoringRun)
    players: dict[int, PlayerGameContext] = field(default_factory=dict)
    quarter: int = 1
    home_score: int = 0
    away_score: int = 0

    def get_player(self, player_id: int, player_name: str = "") -> PlayerGameContext:
        if player_id not in self.players:
            self.players[player_id] = PlayerGameContext(
                player_id=player_id, player_name=player_name,
            )
        return self.players[player_id]

    def on_score(self, team_name: str, player_id: int, player_name: str,
                 points: int, is_three: bool) -> list[str]:
        """Record a score and return any context strings to include in narration."""
        ctx_strings: list[str] = []

        self.scoring_run.add_score(team_name, points)
        if self.scoring_run.is_significant:
            ctx_strings.append(
                f"That's {self.scoring_run.points} straight for {team_name}!"
            )

        pctx = self.get_player(player_id, player_name)
        pctx.on_made_shot(points, is_three)

        # Point milestones
        milestone = pctx.next_milestone
        if milestone:
            pctx.announced_milestones.add(milestone)
            ctx_strings.append(f"That's {milestone} for {player_name}!")

        # Shooting streak
        if pctx.consecutive_makes >= 4:
            ctx_strings.append(f"He can't miss! {pctx.consecutive_makes} in a row!")

        if is_three and pctx.three_made >= 4:
            ctx_strings.append(
                f"He's {pctx.three_made}-for-{pctx.three_attempted} from deep!"
            )

        return ctx_strings
