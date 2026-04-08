"""Standings screen -- full conference/division standings."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.standings_table import StandingsTable


class StandingsScreen(Screen):
    """Full conference/division standings from TeamRecord data."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, standings: Standings) -> None:
        super().__init__()
        self.standings = standings

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="standings-screen"):
            yield Label("League Standings", classes="screen-header")
            yield Button("< Back", id="btn-back", classes="back-button")

            yield Label("Eastern Conference", classes="conference-header")
            east_records = self.standings.conference_standings("East")
            yield StandingsTable(records=east_records, conference="East", id="east-standings")

            yield Label("Western Conference", classes="conference-header")
            west_records = self.standings.conference_standings("West")
            yield StandingsTable(records=west_records, conference="West", id="west-standings")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
