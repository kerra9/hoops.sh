"""Team Dashboard screen -- roster list, team stats, salary cap, depth chart."""

from __future__ import annotations

from hoops_sim.models.league import League
from hoops_sim.models.team import Team
from hoops_sim.tui.base import Screen
from hoops_sim.tui.theme import energy_color
from hoops_sim.tui.widgets.depth_chart import DepthChart
from hoops_sim.tui.widgets.salary_cap_bar import SalaryCapBar
from hoops_sim.tui.widgets.team_stats_panel import TeamStatsPanel


class TeamDashboardScreen(Screen):
    """Roster list, team stats summary, salary cap status, depth chart."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("r", "roster_mgmt", "Roster Mgmt"),
    ]

    def __init__(self, team: Team, league: League) -> None:
        super().__init__()
        self.team = team
        self.league = league

    def render(self) -> str:
        lines = [
            f"[bold]{self.team.full_name} Dashboard[/]",
            "",
            f"  Avg OVR: {self.team.average_overall():.0f}  |  "
            f"Avg Age: {self.team.average_age():.1f}  |  "
            f"Roster: {self.team.roster_size()} players",
            "",
        ]

        # Salary cap bar
        scb = SalaryCapBar(payroll=self.team.total_payroll(), cap_info=self.league.salary_cap)
        lines.append(scb.render())
        lines.append("")

        # Roster table
        lines.append("[bold]ROSTER[/]")
        lines.append(
            f"{'#':>3} {'Name':<22} {'Pos':<4} {'Age':>3} {'OVR':>3} {'HGT':>6} Energy"
        )
        for player in sorted(self.team.roster, key=lambda p: p.overall, reverse=True):
            height_ft = player.body.height_inches // 12
            height_in = player.body.height_inches % 12
            e_pct = player.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 5)
            e_filled = "\u2588" * e_bar
            e_empty = "\u2591" * (5 - e_bar)
            energy_str = f"[{e_color}]{e_filled}{e_empty}[/]"

            lines.append(
                f"{player.jersey_number:>3} {player.full_name:<22} "
                f"{player.position.value:<4} {player.age:>3} {player.overall:>3} "
                f"{height_ft}'{height_in}\"  {energy_str}"
            )

        lines.append("")

        # Team stats
        tsp = TeamStatsPanel()
        lines.append(tsp.render())
        lines.append("")

        # Depth chart
        depth = self._build_depth_chart()
        dc = DepthChart(depth=depth)
        lines.append(dc.render())

        lines.append("")
        lines.append("  [bold green][R][/] Roster Mgmt  [bold red][B][/] Back")
        return "\n".join(lines)

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

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "b":
            self.action_go_back()
        elif c == "r":
            self.action_roster_mgmt()

    def action_roster_mgmt(self) -> None:
        from hoops_sim.tui.screens.roster_mgmt import RosterManagementScreen

        self.app.push_screen(RosterManagementScreen(team=self.team))

    def action_go_back(self) -> None:
        self.app.pop_screen()
