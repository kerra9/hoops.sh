"""Roster Management screen -- lineup ordering, starter/bench assignment."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.models.team import Team


class RosterManagementScreen(Screen):
    """Lineup ordering, starter/bench assignment.

    Reads/writes Team.roster ordering.
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, team: Team) -> None:
        super().__init__()
        self.team = team

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="roster-mgmt"):
            yield Label(f"{self.team.full_name} -- Roster Management", classes="screen-header")
            yield Button("< Back", id="btn-back", classes="back-button")

            yield Label("Starters (top 5 by OVR)", classes="conference-header")
            starters_table = DataTable(id="starters-table")
            starters_table.add_columns("#", "Name", "Pos", "OVR", "Age")
            yield starters_table

            yield Label("Bench", classes="conference-header")
            bench_table = DataTable(id="bench-table")
            bench_table.add_columns("#", "Name", "Pos", "OVR", "Age")
            yield bench_table
        yield Footer()

    def on_mount(self) -> None:
        starters = self.team.get_starters()
        starter_ids = {p.id for p in starters}
        bench = [p for p in self.team.roster if p.id not in starter_ids]

        starters_table = self.query_one("#starters-table", DataTable)
        for p in starters:
            starters_table.add_row(
                str(p.jersey_number), p.full_name, p.position.value,
                str(p.overall), str(p.age),
            )

        bench_table = self.query_one("#bench-table", DataTable)
        for p in sorted(bench, key=lambda x: x.overall, reverse=True):
            bench_table.add_row(
                str(p.jersey_number), p.full_name, p.position.value,
                str(p.overall), str(p.age),
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
