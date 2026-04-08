"""Box Score screen -- full traditional + advanced stats."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.models.stats import TeamGameStats


class BoxScoreScreen(Screen):
    """Traditional + advanced box score from PlayerGameStats / TeamGameStats.

    Accessible mid-game and post-game.
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(
        self,
        home_stats: TeamGameStats,
        away_stats: TeamGameStats,
        home_name: str = "Home",
        away_name: str = "Away",
    ) -> None:
        super().__init__()
        self._home_stats = home_stats
        self._away_stats = away_stats
        self._home_name = home_name
        self._away_name = away_name

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="box-score-screen"):
            yield Label("Box Score", classes="screen-header")
            yield Button("< Back", id="btn-back", classes="back-button")

            yield Label(f"\n{self._away_name}", classes="conference-header")
            away_table = DataTable(id="away-box-table")
            away_table.add_columns(
                "Player", "MIN", "PTS", "REB", "AST", "STL", "BLK",
                "FGM-A", "3PM-A", "FTM-A", "TO", "+/-",
            )
            yield away_table

            yield Label(f"\n{self._home_name}", classes="conference-header")
            home_table = DataTable(id="home-box-table")
            home_table.add_columns(
                "Player", "MIN", "PTS", "REB", "AST", "STL", "BLK",
                "FGM-A", "3PM-A", "FTM-A", "TO", "+/-",
            )
            yield home_table
        yield Footer()

    def on_mount(self) -> None:
        self._populate_table("away-box-table", self._away_stats)
        self._populate_table("home-box-table", self._home_stats)

    def _populate_table(self, table_id: str, team_stats: TeamGameStats) -> None:
        table = self.query_one(f"#{table_id}", DataTable)
        for ps in sorted(
            team_stats.player_stats.values(),
            key=lambda s: s.minutes,
            reverse=True,
        ):
            pm_str = f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            table.add_row(
                ps.player_name[:18],
                f"{ps.minutes:.0f}",
                str(ps.points),
                str(ps.rebounds),
                str(ps.assists),
                str(ps.steals),
                str(ps.blocks),
                f"{ps.fgm}-{ps.fga}",
                f"{ps.three_pm}-{ps.three_pa}",
                f"{ps.ftm}-{ps.fta}",
                str(ps.turnovers),
                pm_str,
            )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
