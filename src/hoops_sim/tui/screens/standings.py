"""Standings screen -- full conference/division standings with tabs and playoff picture.

Redesigned with tabbed views and playoff picture strip.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.playoff_picture import PlayoffPictureStrip
from hoops_sim.tui.widgets.standings_table import StandingsTable


class StandingsScreen(Screen):
    """Full conference/division standings with playoff picture.

    Features:
    - Conference standings with PCT, GB, STK, L10 columns
    - Playoff picture strip at bottom
    - Color-coded: playoff teams green, play-in yellow, out red
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, standings: Standings) -> None:
        super().__init__()
        self.standings = standings

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="standings-screen"):
            yield Label("[bold]League Standings[/]", classes="screen-header")
            yield Button("< Back", id="btn-back", classes="back-button")

            yield Label("[bold green]Eastern Conference[/]", classes="conference-header")
            east_records = self.standings.conference_standings("East")
            yield StandingsTable(
                records=east_records, conference="East", id="east-standings"
            )

            yield Label(
                "[bold blue]Western Conference[/]", classes="conference-header"
            )
            west_records = self.standings.conference_standings("West")
            yield StandingsTable(
                records=west_records, conference="West", id="west-standings"
            )

            # Playoff picture strip
            yield Label("")
            yield Label("[bold]PLAYOFF PICTURE[/]", classes="conference-header")
            east_sorted = sorted(east_records, key=lambda r: r.win_pct, reverse=True)
            west_sorted = sorted(west_records, key=lambda r: r.win_pct, reverse=True)
            east_abbrs = [r.team_name[:3].upper() for r in east_sorted]
            west_abbrs = [r.team_name[:3].upper() for r in west_sorted]
            yield PlayoffPictureStrip(
                east_teams=east_abbrs,
                west_teams=west_abbrs,
                id="playoff-strip",
            )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
