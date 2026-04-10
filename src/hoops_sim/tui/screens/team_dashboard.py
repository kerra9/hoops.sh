"""Team Dashboard screen -- roster list, team stats, salary cap, depth chart.

Textual Screen with DataTable, ProgressBar, and grid layout.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from hoops_sim.models.league import League
from hoops_sim.models.team import Team
from hoops_sim.tui.theme import energy_color
from hoops_sim.tui.widgets.depth_chart import DepthChart
from hoops_sim.tui.widgets.salary_cap_bar import SalaryCapBar
from hoops_sim.tui.widgets.team_stats_panel import TeamStatsPanel


class TeamDashboardScreen(Screen):
    """Roster list, team stats summary, salary cap status, depth chart."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("b", "go_back", "Back"),
        Binding("r", "roster_mgmt", "Roster Mgmt", show=True),
    ]

    def __init__(self, team: Team, league: League) -> None:
        super().__init__()
        self.team = team
        self.league = league

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="team-dashboard"):
            yield Static(
                f"[bold]{self.team.full_name} Dashboard[/]\n\n"
                f"  Avg OVR: {self.team.average_overall():.0f}  |  "
                f"Avg Age: {self.team.average_age():.1f}  |  "
                f"Roster: {self.team.roster_size()} players",
                markup=True,
            )

            yield SalaryCapBar(
                payroll=self.team.total_payroll(),
                cap_info=self.league.salary_cap,
            )

            yield Static("\n[bold]ROSTER[/]", markup=True)
            yield self._build_roster_table()

            yield TeamStatsPanel()

            depth = self._build_depth_chart()
            yield DepthChart(depth=depth)
        yield Footer()

    def _build_roster_table(self) -> DataTable:
        table = DataTable(id="roster-table")
        table.add_columns("#", "Name", "Pos", "Age", "OVR", "HGT", "Energy")
        for player in sorted(self.team.roster, key=lambda p: p.overall, reverse=True):
            height_ft = player.body.height_inches // 12
            height_in = player.body.height_inches % 12
            e_pct = player.current_energy / 100.0
            e_bar = int(e_pct * 5)
            e_filled = "\u2588" * e_bar
            e_empty = "\u2591" * (5 - e_bar)

            table.add_row(
                str(player.jersey_number),
                player.full_name[:22],
                player.position.value,
                str(player.age),
                str(player.overall),
                f"{height_ft}'{height_in}\"",
                f"{e_filled}{e_empty}",
            )
        return table

    def _build_depth_chart(self):
        from hoops_sim.models.player import Position

        depth = {"PG": [], "SG": [], "SF": [], "PF": [], "C": []}
        pos_map = {
            Position.POINT_GUARD: "PG",
            Position.SHOOTING_GUARD: "SG",
            Position.SMALL_FORWARD: "SF",
            Position.POWER_FORWARD: "PF",
            Position.CENTER: "C",
        }
        for player in sorted(self.team.roster, key=lambda p: p.overall, reverse=True):
            pos_key = pos_map.get(player.position, "SF")
            if len(depth[pos_key]) < 2:
                depth[pos_key].append(player.last_name)
        return depth

    def action_roster_mgmt(self) -> None:
        from hoops_sim.tui.screens.roster_mgmt import RosterManagementScreen

        self.app.push_screen(RosterManagementScreen(team=self.team))

    def action_go_back(self) -> None:
        self.app.pop_screen()
