"""Team Dashboard screen -- roster list, team stats, salary cap, depth chart.

Redesigned with depth chart, team stats panel, salary cap with tax marker,
and inline energy gauges per player.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.models.league import League
from hoops_sim.models.team import Team
from hoops_sim.tui.theme import energy_color
from hoops_sim.tui.widgets.depth_chart import DepthChart
from hoops_sim.tui.widgets.salary_cap_bar import SalaryCapBar
from hoops_sim.tui.widgets.team_stats_panel import TeamStatsPanel


class TeamDashboardScreen(Screen):
    """Roster list, team stats summary, salary cap status, depth chart.

    Dense layout with:
    - Record + conference rank in header
    - Salary cap bar with luxury tax marker
    - Roster table with inline energy gauges
    - Side panels: team stats + depth chart
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "roster_mgmt", "Roster Mgmt"),
    ]

    def __init__(self, team: Team, league: League) -> None:
        super().__init__()
        self.team = team
        self.league = league

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="team-dashboard"):
            yield Label(
                f"[bold]{self.team.full_name} Dashboard[/]",
                id="team-header",
            )
            yield Button("< Back", id="btn-back", classes="back-button")

            # Team info line
            yield Label(
                f"  Avg OVR: {self.team.average_overall():.0f}  |  "
                f"Avg Age: {self.team.average_age():.1f}  |  "
                f"Roster: {self.team.roster_size()} players"
            )

            # Salary cap bar
            yield SalaryCapBar(
                payroll=self.team.total_payroll(),
                cap_info=self.league.salary_cap,
                id="team-salary-bar",
            )

            with Horizontal():
                # Left: Roster table
                with Vertical():
                    yield Label("[bold]ROSTER[/]", classes="section-title")
                    table = DataTable(id="roster-table")
                    table.add_columns(
                        "#", "Name", "Pos", "Age", "OVR", "HGT", "Energy"
                    )
                    yield table

                    yield Button(
                        "Roster Management",
                        id="btn-roster-mgmt",
                        variant="primary",
                    )

                # Right: Team stats + depth chart
                with Vertical():
                    yield TeamStatsPanel(id="team-stats-panel")
                    yield Label("")
                    depth = self._build_depth_chart()
                    yield DepthChart(depth=depth, id="team-depth")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#roster-table", DataTable)
        for player in sorted(
            self.team.roster, key=lambda p: p.overall, reverse=True
        ):
            height_ft = player.body.height_inches // 12
            height_in = player.body.height_inches % 12
            # Inline energy gauge (5-char bar)
            e_pct = player.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 5)
            e_filled = "\u2588" * e_bar
            e_empty = "\u2591" * (5 - e_bar)
            energy_str = f"[{e_color}]{e_filled}{e_empty}[/]"

            table.add_row(
                str(player.jersey_number),
                player.full_name,
                player.position.value,
                str(player.age),
                str(player.overall),
                f"{height_ft}'{height_in}\"",
                energy_str,
                key=str(player.id),
            )

    def _build_depth_chart(self):
        """Build position-based depth chart from roster."""
        from hoops_sim.models.player import Position

        depth = {"PG": [], "SG": [], "SF": [], "PF": [], "C": []}
        pos_map = {
            Position.POINT_GUARD: "PG",
            Position.SHOOTING_GUARD: "SG",
            Position.SMALL_FORWARD: "SF",
            Position.POWER_FORWARD: "PF",
            Position.CENTER: "C",
        }
        for player in sorted(
            self.team.roster, key=lambda p: p.overall, reverse=True
        ):
            pos_key = pos_map.get(player.position, "SF")
            if len(depth[pos_key]) < 2:
                depth[pos_key].append(player.last_name)
        return depth

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """Open player card when a row is selected."""
        if event.row_key and event.row_key.value is not None:
            player_id = int(event.row_key.value)
            player = self.team.get_player(player_id)
            if player:
                from hoops_sim.tui.screens.player_card import PlayerCardScreen

                self.app.push_screen(PlayerCardScreen(player=player))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()
        elif event.button.id == "btn-roster-mgmt":
            self.action_roster_mgmt()

    def action_roster_mgmt(self) -> None:
        from hoops_sim.tui.screens.roster_mgmt import RosterManagementScreen

        self.app.push_screen(RosterManagementScreen(team=self.team))

    def action_go_back(self) -> None:
        self.app.pop_screen()
