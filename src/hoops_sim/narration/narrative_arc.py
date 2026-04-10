"""Narrative arc detection -- identifies storylines developing during the game.

Tracks comeback arcs, blowouts, star performances, hot/cold streaks,
foul trouble drama, and clock management situations.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from hoops_sim.narration.stat_tracker import LiveStatTracker


class ArcType(enum.Enum):
    """Types of narrative arcs."""

    COMEBACK = "comeback"
    BLOWOUT = "blowout"
    STAR_PERFORMANCE = "star_performance"
    HOT_STREAK = "hot_streak"
    COLD_SPELL = "cold_spell"
    FOUL_TROUBLE = "foul_trouble"
    CLOSE_GAME = "close_game"
    BACK_AND_FORTH = "back_and_forth"
    CLOCK_MANAGEMENT = "clock_management"


@dataclass
class NarrativeArc:
    """A single narrative arc instance."""

    arc_type: ArcType
    team_or_player: str
    intensity: float = 0.0  # 0.0 to 1.0
    description: str = ""
    started_at_clock: float = 0.0
    last_updated_clock: float = 0.0

    @property
    def is_active(self) -> bool:
        return self.intensity > 0.2


@dataclass
class ArcSnapshot:
    """A snapshot of the most relevant arcs at a point in time."""

    primary_arc: Optional[NarrativeArc] = None
    secondary_arcs: List[NarrativeArc] = field(default_factory=list)

    @property
    def has_active_arc(self) -> bool:
        return self.primary_arc is not None and self.primary_arc.is_active


class NarrativeArcTracker:
    """Identifies and tracks narrative arcs throughout a game."""

    def __init__(
        self, home_team: str, away_team: str, stat_tracker: LiveStatTracker,
    ) -> None:
        self.home_team = home_team
        self.away_team = away_team
        self.stats = stat_tracker
        self.arcs: List[NarrativeArc] = []
        self._max_lead_home = 0
        self._max_lead_away = 0
        self._prev_lead = 0

    def update(self, quarter: int, game_clock: float) -> ArcSnapshot:
        """Update arc tracking and return the current snapshot."""
        self.arcs = []
        diff = self.stats.home_score - self.stats.away_score

        # Track max leads
        if diff > self._max_lead_home:
            self._max_lead_home = diff
        if -diff > self._max_lead_away:
            self._max_lead_away = -diff

        self._check_comeback(diff, quarter, game_clock)
        self._check_blowout(diff, quarter, game_clock)
        self._check_close_game(diff, quarter, game_clock)
        self._check_star_performances(quarter, game_clock)
        self._check_foul_trouble(quarter, game_clock)
        self._check_clock_management(quarter, game_clock)

        self._prev_lead = diff

        # Sort by intensity and return snapshot
        active = [a for a in self.arcs if a.is_active]
        active.sort(key=lambda a: a.intensity, reverse=True)

        snapshot = ArcSnapshot()
        if active:
            snapshot.primary_arc = active[0]
            snapshot.secondary_arcs = active[1:3]
        return snapshot

    def _check_comeback(
        self, diff: int, quarter: int, game_clock: float,
    ) -> None:
        """Check for comeback arcs."""
        # Home comeback: was down big, now close
        if self._max_lead_away >= 12 and diff > -5:
            comeback_pct = 1.0 - max(0, -diff) / self._max_lead_away
            self.arcs.append(NarrativeArc(
                arc_type=ArcType.COMEBACK,
                team_or_player=self.home_team,
                intensity=min(1.0, comeback_pct * 0.8),
                description=(
                    f"{self.home_team} was down {self._max_lead_away}, "
                    f"now {'tied' if diff == 0 else ('up ' + str(diff) if diff > 0 else 'within ' + str(-diff))}"
                ),
                last_updated_clock=game_clock,
            ))

        # Away comeback
        if self._max_lead_home >= 12 and diff < 5:
            comeback_pct = 1.0 - max(0, diff) / self._max_lead_home
            self.arcs.append(NarrativeArc(
                arc_type=ArcType.COMEBACK,
                team_or_player=self.away_team,
                intensity=min(1.0, comeback_pct * 0.8),
                description=(
                    f"{self.away_team} was down {self._max_lead_home}, "
                    f"now {'tied' if diff == 0 else ('up ' + str(-diff) if diff < 0 else 'within ' + str(diff))}"
                ),
                last_updated_clock=game_clock,
            ))

    def _check_blowout(
        self, diff: int, quarter: int, game_clock: float,
    ) -> None:
        """Check for blowout arcs."""
        abs_diff = abs(diff)
        if abs_diff >= 20 and quarter >= 3:
            leading = self.home_team if diff > 0 else self.away_team
            trailing = self.away_team if diff > 0 else self.home_team
            self.arcs.append(NarrativeArc(
                arc_type=ArcType.BLOWOUT,
                team_or_player=trailing,
                intensity=min(1.0, abs_diff / 30.0),
                description=f"{leading} running away with it, up {abs_diff}",
                last_updated_clock=game_clock,
            ))

    def _check_close_game(
        self, diff: int, quarter: int, game_clock: float,
    ) -> None:
        """Check for close game tension."""
        abs_diff = abs(diff)
        if quarter >= 4 and abs_diff <= 5:
            intensity = (1.0 - abs_diff / 6.0) * (1.0 - game_clock / 720.0)
            if intensity > 0.3:
                self.arcs.append(NarrativeArc(
                    arc_type=ArcType.CLOSE_GAME,
                    team_or_player="both",
                    intensity=min(1.0, intensity),
                    description=f"Tight game in the 4th, {abs_diff}-point difference",
                    last_updated_clock=game_clock,
                ))

    def _check_star_performances(
        self, quarter: int, game_clock: float,
    ) -> None:
        """Check for standout player performances."""
        for pid, pstats in self.stats.players.items():
            # Big scoring night
            if pstats.points >= 30:
                intensity = min(1.0, pstats.points / 45.0)
                self.arcs.append(NarrativeArc(
                    arc_type=ArcType.STAR_PERFORMANCE,
                    team_or_player=pstats.player_name,
                    intensity=intensity,
                    description=f"{pstats.player_name} with {pstats.points} points",
                    last_updated_clock=game_clock,
                ))
            # Hot shooting streak
            if pstats.consecutive_makes >= 4:
                self.arcs.append(NarrativeArc(
                    arc_type=ArcType.HOT_STREAK,
                    team_or_player=pstats.player_name,
                    intensity=min(1.0, pstats.consecutive_makes / 6.0),
                    description=(
                        f"{pstats.player_name} has made "
                        f"{pstats.consecutive_makes} in a row"
                    ),
                    last_updated_clock=game_clock,
                ))

    def _check_foul_trouble(
        self, quarter: int, game_clock: float,
    ) -> None:
        """Check for foul trouble drama."""
        for pid, pstats in self.stats.players.items():
            if pstats.personal_fouls >= 4 and quarter <= 3:
                self.arcs.append(NarrativeArc(
                    arc_type=ArcType.FOUL_TROUBLE,
                    team_or_player=pstats.player_name,
                    intensity=min(1.0, pstats.personal_fouls / 5.0),
                    description=(
                        f"{pstats.player_name} with "
                        f"{pstats.personal_fouls} fouls"
                    ),
                    last_updated_clock=game_clock,
                ))

    def _check_clock_management(
        self, quarter: int, game_clock: float,
    ) -> None:
        """Check for end-of-game clock situations."""
        if quarter >= 4 and game_clock < 120.0:
            diff = abs(self.stats.home_score - self.stats.away_score)
            if diff <= 8:
                intensity = (1.0 - game_clock / 120.0) * (1.0 - diff / 10.0)
                self.arcs.append(NarrativeArc(
                    arc_type=ArcType.CLOCK_MANAGEMENT,
                    team_or_player="both",
                    intensity=min(1.0, intensity),
                    description=f"Crunch time! {game_clock:.0f} seconds left",
                    last_updated_clock=game_clock,
                ))
