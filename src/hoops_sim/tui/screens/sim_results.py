"""Sim Results screen -- summary of all games simulated in a day."""

from __future__ import annotations

from typing import Dict, List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.season.schedule import ScheduledGame


class SimResultsScreen(Screen):
    """Summary of all games simulated in a day.

    Shows scores and notable performances.
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("enter", "go_back", "Continue"),
    ]

    def __init__(
        self,
        games: List[ScheduledGame],
        team_names: Dict[int, str],
        day: int = 1,
    ) -> None:
        super().__init__()
        self._games = games
        self._team_names = team_names
        self._day = day

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="sim-results-screen"):
            yield Label(f"Day {self._day} Results", classes="screen-header")

            table = DataTable(id="sim-results-table")
            table.add_columns("Away", "Score", "Home", "Score")
            yield table

            yield Label("")
            yield Button("Continue", id="btn-continue", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#sim-results-table", DataTable)
        for game in self._games:
            if game.played:
                away_name = self._team_names.get(game.away_team_id, f"Team {game.away_team_id}")
                home_name = self._team_names.get(game.home_team_id, f"Team {game.home_team_id}")
                table.add_row(
                    away_name,
                    str(game.away_score),
                    home_name,
                    str(game.home_score),
                )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-continue":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
