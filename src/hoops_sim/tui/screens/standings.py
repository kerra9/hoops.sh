"""Standings screen -- full conference/division standings with playoff picture."""

from __future__ import annotations

from hoops_sim.season.standings import Standings
from hoops_sim.tui.base import Screen
from hoops_sim.tui.widgets.playoff_picture import PlayoffPictureStrip
from hoops_sim.tui.widgets.standings_table import StandingsTable


class StandingsScreen(Screen):
    """Full conference/division standings with playoff picture."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, standings: Standings) -> None:
        super().__init__()
        self.standings = standings

    def render(self) -> str:
        lines = ["[bold]League Standings[/]", ""]

        lines.append("[bold green]Eastern Conference[/]")
        east_records = self.standings.conference_standings("East")
        east_table = StandingsTable(records=east_records, conference="East")
        lines.append(east_table.render())

        lines.append("")
        lines.append("[bold blue]Western Conference[/]")
        west_records = self.standings.conference_standings("West")
        west_table = StandingsTable(records=west_records, conference="West")
        lines.append(west_table.render())

        lines.append("")
        lines.append("[bold]PLAYOFF PICTURE[/]")
        east_sorted = sorted(east_records, key=lambda r: r.win_pct, reverse=True)
        west_sorted = sorted(west_records, key=lambda r: r.win_pct, reverse=True)
        east_abbrs = [r.team_name[:3].upper() for r in east_sorted]
        west_abbrs = [r.team_name[:3].upper() for r in west_sorted]
        strip = PlayoffPictureStrip(east_teams=east_abbrs, west_teams=west_abbrs)
        lines.append(strip.render())

        lines.append("\n  [bold red][B][/] Back")
        return "\n".join(lines)

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "b":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
