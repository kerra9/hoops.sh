"""Standings screen -- full conference/division standings with playoff picture.

Textual Screen with TabbedContent and DataTable widgets.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.playoff_picture import PlayoffPictureStrip
from hoops_sim.tui.widgets.standings_table import StandingsTableWidget


class StandingsScreen(Screen):
    """Full conference/division standings with playoff picture."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("b", "go_back", "Back"),
    ]

    def __init__(self, standings: Standings) -> None:
        super().__init__()
        self.standings = standings

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="standings"):
            yield Static("[bold]League Standings[/]", markup=True)

            yield Static("\n[bold green]Eastern Conference[/]", markup=True)
            east_records = self.standings.conference_standings("East")
            yield StandingsTableWidget(records=east_records, conference="East")

            yield Static("\n[bold blue]Western Conference[/]", markup=True)
            west_records = self.standings.conference_standings("West")
            yield StandingsTableWidget(records=west_records, conference="West")

            yield Static("\n[bold]PLAYOFF PICTURE[/]", markup=True)
            east_sorted = sorted(east_records, key=lambda r: r.win_pct, reverse=True)
            west_sorted = sorted(west_records, key=lambda r: r.win_pct, reverse=True)
            east_abbrs = [r.team_name[:3].upper() for r in east_sorted]
            west_abbrs = [r.team_name[:3].upper() for r in west_sorted]
            yield PlayoffPictureStrip(east_teams=east_abbrs, west_teams=west_abbrs)
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()
