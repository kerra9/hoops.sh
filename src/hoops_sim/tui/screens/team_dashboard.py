"""Team Dashboard screen -- roster list, team stats, salary cap."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.models.league import League
from hoops_sim.models.team import Team
from hoops_sim.tui.widgets.salary_cap_bar import SalaryCapBar


class TeamDashboardScreen(Screen):
    """Roster list, team stats summary, salary cap status.

    Reads from Team and League models.
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
                f"{self.team.full_name} Dashboard",
                id="team-header",
            )
            yield Button("< Back", id="btn-back", classes="back-button")

            # Team info
            yield Label(
                f"Avg OVR: {self.team.average_overall():.0f}  "
                f"Avg Age: {self.team.average_age():.1f}  "
                f"Roster: {self.team.roster_size()} players"
            )

            # Salary cap bar
            yield SalaryCapBar(
                payroll=self.team.total_payroll(),
                cap_info=self.league.salary_cap,
                id="team-salary-bar",
            )

            # Roster table
            yield Label("Roster", classes="conference-header")
            table = DataTable(id="roster-table")
            table.add_columns("#", "Name", "Pos", "Age", "OVR", "HGT", "WGT")
            yield table

            yield Button("Roster Management", id="btn-roster-mgmt", variant="primary")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#roster-table", DataTable)
        for player in sorted(self.team.roster, key=lambda p: p.overall, reverse=True):
            height_ft = player.body.height_inches // 12
            height_in = player.body.height_inches % 12
            table.add_row(
                str(player.jersey_number),
                player.full_name,
                player.position.value,
                str(player.age),
                str(player.overall),
                f"{height_ft}'{height_in}\"",
                f"{player.body.weight_lbs} lbs",
                key=str(player.id),
            )

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
