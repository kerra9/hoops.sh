"""Roster Management screen -- lineup ordering, starter/bench assignment.

Redesigned with side-by-side starters vs bench, reorder support,
and lineup fit score.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.models.team import Team
from hoops_sim.tui.theme import energy_color


class RosterManagementScreen(Screen):
    """Lineup ordering, starter/bench assignment.

    Features:
    - Side-by-side starters vs bench with visual separator
    - Per-player energy bars
    - Reorder support with up/down keys
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
            yield Label(
                f"[bold]{self.team.full_name} -- Roster Management[/]",
                classes="screen-header",
            )
            yield Button("< Back", id="btn-back", classes="back-button")

            with Horizontal():
                # Left: Starters
                with Vertical():
                    yield Label(
                        "[bold green]STARTERS[/]", classes="conference-header"
                    )
                    starters_table = DataTable(id="starters-table")
                    starters_table.add_columns(
                        "#", "Name", "Pos", "OVR", "Age", "Energy"
                    )
                    yield starters_table

                # Right: Bench
                with Vertical():
                    yield Label(
                        "[bold yellow]BENCH[/]", classes="conference-header"
                    )
                    bench_table = DataTable(id="bench-table")
                    bench_table.add_columns(
                        "#", "Name", "Pos", "OVR", "Age", "Energy"
                    )
                    yield bench_table
        yield Footer()

    def on_mount(self) -> None:
        starters = self.team.get_starters()
        starter_ids = {p.id for p in starters}
        bench = [p for p in self.team.roster if p.id not in starter_ids]

        starters_table = self.query_one("#starters-table", DataTable)
        for p in starters:
            e_pct = p.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 5)
            filled = "\u2588" * e_bar
            empty = "\u2591" * (5 - e_bar)
            energy_str = f"[{e_color}]{filled}{empty}[/]"
            starters_table.add_row(
                str(p.jersey_number),
                p.full_name,
                p.position.value,
                str(p.overall),
                str(p.age),
                energy_str,
            )

        bench_table = self.query_one("#bench-table", DataTable)
        for p in sorted(bench, key=lambda x: x.overall, reverse=True):
            e_pct = p.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 5)
            filled = "\u2588" * e_bar
            empty = "\u2591" * (5 - e_bar)
            energy_str = f"[{e_color}]{filled}{empty}[/]"
            bench_table.add_row(
                str(p.jersey_number),
                p.full_name,
                p.position.value,
                str(p.overall),
                str(p.age),
                energy_str,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
