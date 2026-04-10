"""Live stat tracking for narration context.

Maintains running stat lines for every player and both teams,
providing narration-friendly data like shooting percentages,
ordinal assists, and scoring run tracking.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from hoops_sim.narration.templates.context_suffixes import ordinal


@dataclass
class PlayerNarrationStats:
    """Live stats for one player, optimized for narration queries."""

    player_id: int
    player_name: str
    points: int = 0
    fg_made: int = 0
    fg_attempted: int = 0
    three_made: int = 0
    three_attempted: int = 0
    ft_made: int = 0
    ft_attempted: int = 0
    assists: int = 0
    rebounds: int = 0
    offensive_rebounds: int = 0
    steals: int = 0
    blocks: int = 0
    turnovers: int = 0
    personal_fouls: int = 0
    consecutive_makes: int = 0
    consecutive_misses: int = 0
    minutes_played: float = 0.0
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

    def on_made_ft(self) -> None:
        self.points += 1
        self.ft_made += 1
        self.ft_attempted += 1

    def on_missed_ft(self) -> None:
        self.ft_attempted += 1

    @property
    def is_hot(self) -> bool:
        return self.consecutive_makes >= 3

    @property
    def is_cold(self) -> bool:
        return self.consecutive_misses >= 4

    @property
    def fg_pct(self) -> float:
        if self.fg_attempted == 0:
            return 0.0
        return self.fg_made / self.fg_attempted

    @property
    def three_pct(self) -> float:
        if self.three_attempted == 0:
            return 0.0
        return self.three_made / self.three_attempted

    @property
    def next_milestone(self) -> Optional[int]:
        """Next unannounced scoring milestone (20, 30, 40, 50)."""
        for m in [20, 30, 40, 50]:
            if self.points >= m and m not in self.announced_milestones:
                return m
        return None

    def shooting_line(self) -> str:
        """Human-readable shooting line."""
        base = f"{self.fg_made}-for-{self.fg_attempted}"
        if self.three_attempted > 0:
            base += f", {self.three_made}-for-{self.three_attempted} from three"
        return base

    def stat_line(self) -> str:
        """Full human-readable stat line."""
        parts = [f"{self.points} pts"]
        if self.rebounds > 0:
            parts.append(f"{self.rebounds} reb")
        if self.assists > 0:
            parts.append(f"{self.assists} ast")
        if self.steals > 0:
            parts.append(f"{self.steals} stl")
        if self.blocks > 0:
            parts.append(f"{self.blocks} blk")
        return ", ".join(parts)

    def assist_ordinal(self) -> str:
        return ordinal(self.assists)

    @property
    def is_in_foul_trouble(self) -> bool:
        return self.personal_fouls >= 4


@dataclass
class TeamNarrationStats:
    """Live team-level stats for narration."""

    team_name: str
    points: int = 0
    fg_made: int = 0
    fg_attempted: int = 0
    three_made: int = 0
    three_attempted: int = 0
    turnovers: int = 0
    points_in_paint: int = 0
    fast_break_points: int = 0
    second_chance_points: int = 0

    @property
    def fg_pct(self) -> float:
        if self.fg_attempted == 0:
            return 0.0
        return self.fg_made / self.fg_attempted

    @property
    def three_pct(self) -> float:
        if self.three_attempted == 0:
            return 0.0
        return self.three_made / self.three_attempted


@dataclass
class ScoringRunTracker:
    """Tracks scoring runs and droughts for both teams."""

    current_run_team: str = ""
    current_run_points: int = 0
    current_run_against: int = 0
    last_score_time: float = 0.0
    home_last_score_clock: float = 720.0
    away_last_score_clock: float = 720.0

    def on_score(self, team: str, points: int, game_clock: float) -> None:
        if team == self.current_run_team:
            self.current_run_points += points
        else:
            self.current_run_team = team
            self.current_run_points = points
            self.current_run_against = 0
        self.last_score_time = game_clock

    def on_opponent_score(self, team: str, points: int) -> None:
        """Track points against during the current run."""
        if team != self.current_run_team:
            self.current_run_against += points

    @property
    def is_significant_run(self) -> bool:
        return self.current_run_points >= 7 and self.current_run_against <= 2

    def drought_seconds(self, team: str, current_clock: float) -> float:
        if team == "home":
            return self.home_last_score_clock - current_clock
        return self.away_last_score_clock - current_clock


class LiveStatTracker:
    """Manages all live stat tracking for narration."""

    def __init__(self, home_team: str, away_team: str) -> None:
        self.home_team_name = home_team
        self.away_team_name = away_team
        self.players: Dict[int, PlayerNarrationStats] = {}
        self.home_stats = TeamNarrationStats(team_name=home_team)
        self.away_stats = TeamNarrationStats(team_name=away_team)
        self.scoring_run = ScoringRunTracker()
        self.home_score = 0
        self.away_score = 0
        self.lead_changes = 0
        self.ties = 0
        self.largest_lead_home = 0
        self.largest_lead_away = 0

    def get_player(self, player_id: int, player_name: str = "") -> PlayerNarrationStats:
        if player_id not in self.players:
            self.players[player_id] = PlayerNarrationStats(
                player_id=player_id, player_name=player_name,
            )
        return self.players[player_id]

    def on_made_shot(
        self, player_id: int, player_name: str, is_home: bool,
        points: int, is_three: bool, game_clock: float,
    ) -> List[str]:
        """Record a made shot and return context strings for narration."""
        ctx: List[str] = []
        pstats = self.get_player(player_id, player_name)
        pstats.on_made_shot(points, is_three)

        team_stats = self.home_stats if is_home else self.away_stats
        team_stats.fg_made += 1
        team_stats.fg_attempted += 1
        team_stats.points += points
        if is_three:
            team_stats.three_made += 1
            team_stats.three_attempted += 1

        team_name = self.home_team_name if is_home else self.away_team_name
        self.scoring_run.on_score(team_name, points, game_clock)

        # Update scores
        old_diff = self.home_score - self.away_score
        if is_home:
            self.home_score += points
        else:
            self.away_score += points
        new_diff = self.home_score - self.away_score

        # Lead change detection
        if old_diff * new_diff < 0:
            self.lead_changes += 1
        if new_diff == 0 and old_diff != 0:
            self.ties += 1

        # Track largest leads
        if new_diff > self.largest_lead_home:
            self.largest_lead_home = new_diff
        if -new_diff > self.largest_lead_away:
            self.largest_lead_away = -new_diff

        # Milestone check
        milestone = pstats.next_milestone
        if milestone:
            pstats.announced_milestones.add(milestone)
            ctx.append(f"That's {milestone} for {player_name}!")

        # Hot streak
        if pstats.consecutive_makes >= 4:
            ctx.append(f"{pstats.consecutive_makes} in a row for {player_name}!")

        # Three-point line check
        if is_three and pstats.three_made >= 4:
            ctx.append(
                f"{player_name} is {pstats.three_made}-for-"
                f"{pstats.three_attempted} from deep!"
            )

        # Scoring run
        if self.scoring_run.is_significant_run:
            ctx.append(
                f"{self.scoring_run.current_run_points} straight "
                f"for {team_name}!"
            )

        return ctx

    def on_missed_shot(
        self, player_id: int, player_name: str, is_home: bool, is_three: bool,
    ) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.on_missed_shot(is_three)
        team_stats = self.home_stats if is_home else self.away_stats
        team_stats.fg_attempted += 1
        if is_three:
            team_stats.three_attempted += 1

    def on_assist(self, player_id: int, player_name: str) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.assists += 1

    def on_rebound(
        self, player_id: int, player_name: str, is_offensive: bool,
    ) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.rebounds += 1
        if is_offensive:
            pstats.offensive_rebounds += 1

    def on_steal(self, player_id: int, player_name: str) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.steals += 1

    def on_block(self, player_id: int, player_name: str) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.blocks += 1

    def on_turnover(self, player_id: int, player_name: str) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.turnovers += 1

    def on_foul(self, player_id: int, player_name: str) -> None:
        pstats = self.get_player(player_id, player_name)
        pstats.personal_fouls += 1

    def score_string(self) -> str:
        """Current score as a string."""
        return (
            f"{self.home_team_name} {self.home_score}, "
            f"{self.away_team_name} {self.away_score}"
        )

    def lead_string(self, is_home: bool) -> str:
        """Describe the current lead from a team's perspective."""
        diff = self.home_score - self.away_score
        if diff == 0:
            return "tied"
        if is_home:
            return f"up {diff}" if diff > 0 else f"down {-diff}"
        return f"up {-diff}" if diff < 0 else f"down {diff}"
