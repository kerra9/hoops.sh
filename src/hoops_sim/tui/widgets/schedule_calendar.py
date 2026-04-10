"""Day-by-day game listing with results."""

from __future__ import annotations

from typing import Dict, List

from hoops_sim.season.schedule import ScheduledGame
from hoops_sim.tui.base import Widget


class ScheduleCalendar(Widget):
    """Day-by-day game listing with results."""

    def __init__(
        self,
        games: List[ScheduledGame] | None = None,
        team_names: Dict[int, str] | None = None,
        current_day: int = 1,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._games = games or []
        self._team_names = team_names or {}
        self._current_day = current_day

    def render(self) -> str:
        lines = [f"{'Day':>4} {'Away':<16} {'Score':>10} {'Home':<16} {'Status'}"]
        for game in sorted(self._games, key=lambda g: (g.day, g.game_id)):
            home_name = self._team_names.get(game.home_team_id, f"Team {game.home_team_id}")
            away_name = self._team_names.get(game.away_team_id, f"Team {game.away_team_id}")
            if game.played:
                score = f"{game.away_score} - {game.home_score}"
                status = "Final"
            elif game.day == self._current_day:
                score = "vs"
                status = "Today"
            else:
                score = "vs"
                status = f"Day {game.day}"
            lines.append(f"{game.day:>4} {away_name:<16} {score:>10} {home_name:<16} {status}")
        return "\n".join(lines)

    def update_games(self, games: List[ScheduledGame], current_day: int) -> None:
        """Update the schedule display."""
        self._games = games
        self._current_day = current_day
