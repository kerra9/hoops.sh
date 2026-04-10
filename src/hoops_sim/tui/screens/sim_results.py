"""Sim Results screen -- summary of all games simulated in a day.

Textual Screen with DataTable showing game results.
"""

from __future__ import annotations

from typing import Dict, List

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from hoops_sim.season.schedule import ScheduledGame
from hoops_sim.tui.theme import SCORE_GREEN, SCORE_RED


class SimResultsScreen(Screen):
    """Summary of all games simulated in a day."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("enter", "go_back", "Continue"),
    ]

    def __init__(
        self,
        games: List[ScheduledGame],
        team_names: Dict[int, str],
        day: int = 1,
        user_team_id: int | None = None,
    ) -> None:
        super().__init__()
        self._games = games
        self._team_names = team_names
        self._day = day
        self._user_team_id = user_team_id

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="sim-results"):
            yield Static(f"[bold]Day {self._day} Results[/]", markup=True)

            table = DataTable(id="results-table")
            table.add_columns("Away", "Score", "Home", "Score", "Result")

            for game in self._games:
                if game.played:
                    away_name = self._team_names.get(
                        game.away_team_id, f"Team {game.away_team_id}"
                    )
                    home_name = self._team_names.get(
                        game.home_team_id, f"Team {game.home_team_id}"
                    )

                    if game.home_score > game.away_score:
                        result = f"{home_name[:12]} W"
                    else:
                        result = f"{away_name[:12]} W"

                    table.add_row(
                        away_name[:16],
                        str(game.away_score),
                        home_name[:16],
                        str(game.home_score),
                        result,
                    )

            yield table
            yield Static("\nPress [bold]Enter[/] or [bold]Escape[/] to continue", markup=True)
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()
