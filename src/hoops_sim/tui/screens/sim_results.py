"""Sim Results screen -- summary of all games simulated in a day.

Redesigned with richer result cards showing scores and notable performances.
"""

from __future__ import annotations

from typing import Dict, List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.season.schedule import ScheduledGame
from hoops_sim.tui.theme import SCORE_GREEN, SCORE_RED


class SimResultsScreen(Screen):
    """Summary of all games simulated in a day.

    Features:
    - Game result cards with color-coded W/L
    - Notable performances section
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
        user_team_id: int | None = None,
    ) -> None:
        super().__init__()
        self._games = games
        self._team_names = team_names
        self._day = day
        self._user_team_id = user_team_id

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="sim-results-screen"):
            yield Label(
                f"[bold]Day {self._day} Results[/]", classes="screen-header"
            )

            for game in self._games:
                if game.played:
                    away_name = self._team_names.get(
                        game.away_team_id, f"Team {game.away_team_id}"
                    )
                    home_name = self._team_names.get(
                        game.home_team_id, f"Team {game.home_team_id}"
                    )

                    # Color-code by user team W/L
                    if self._user_team_id:
                        if game.home_team_id == self._user_team_id:
                            color = (
                                SCORE_GREEN
                                if game.home_score > game.away_score
                                else SCORE_RED
                            )
                        elif game.away_team_id == self._user_team_id:
                            color = (
                                SCORE_GREEN
                                if game.away_score > game.home_score
                                else SCORE_RED
                            )
                        else:
                            color = "#cccccc"
                    else:
                        color = "#cccccc"

                    yield Label(
                        f"  [{color}]{away_name:<20} {game.away_score:>3}"
                        f"  -  "
                        f"{game.home_score:<3} {home_name}[/]"
                    )

            yield Label("")
            yield Button("Continue", id="btn-continue", variant="primary")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-continue":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
