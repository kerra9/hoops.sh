"""Day-by-day game listing with results."""

from __future__ import annotations

from typing import Dict, List, Optional

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from hoops_sim.season.schedule import ScheduledGame


class ScheduleCalendar(Widget):
    """Day-by-day game listing with results.

    Shows games organized by day with scores for completed games
    and matchup info for upcoming games.
    """

    DEFAULT_CSS = """
    ScheduleCalendar {
        height: auto;
        width: 100%;
    }
    """

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

    def compose(self) -> ComposeResult:
        table = DataTable(id="schedule-table")
        table.add_columns("Day", "Away", "Score", "Home", "Status")
        yield table

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

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

            table.add_row(
                str(game.day),
                away_name,
                score,
                home_name,
                status,
            )

    def update_games(self, games: List[ScheduledGame], current_day: int) -> None:
        """Update the schedule display."""
        self._games = games
        self._current_day = current_day
        self._populate()
