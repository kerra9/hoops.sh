"""Roster Management screen -- lineup ordering, starter/bench assignment.

Textual Screen with DataTable for roster management.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from hoops_sim.models.team import Team
from hoops_sim.tui.theme import energy_color


class RosterManagementScreen(Screen):
    """Lineup ordering, starter/bench assignment."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("b", "go_back", "Back"),
    ]

    def __init__(self, team: Team) -> None:
        super().__init__()
        self.team = team

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="roster-mgmt"):
            yield Static(
                f"[bold]{self.team.full_name} -- Roster Management[/]",
                markup=True,
            )

            starters = self.team.get_starters()
            starter_ids = {p.id for p in starters}
            bench = [p for p in self.team.roster if p.id not in starter_ids]

            # Starters
            yield Static("\n[bold green]STARTERS[/]", markup=True)
            yield self._build_table(starters, "starters-table")

            # Bench
            yield Static("\n[bold yellow]BENCH[/]", markup=True)
            bench_sorted = sorted(bench, key=lambda x: x.overall, reverse=True)
            yield self._build_table(bench_sorted, "bench-table")
        yield Footer()

    def _build_table(self, players, table_id: str) -> DataTable:
        table = DataTable(id=table_id)
        table.add_columns("#", "Name", "Pos", "OVR", "Age", "Energy")
        for p in players:
            e_pct = p.current_energy / 100.0
            e_bar = int(e_pct * 5)
            filled = "\u2588" * e_bar
            empty = "\u2591" * (5 - e_bar)

            table.add_row(
                str(p.jersey_number),
                p.full_name[:22],
                p.position.value,
                str(p.overall),
                str(p.age),
                f"{filled}{empty}",
            )
        return table

    def action_go_back(self) -> None:
        self.app.pop_screen()
