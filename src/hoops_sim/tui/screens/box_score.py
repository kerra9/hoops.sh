"""Box Score screen -- tabbed traditional + advanced stats.

Redesigned with tabbed interface and quarter scoring breakdown.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, DataTable, Footer, Header, Label

from hoops_sim.models.stats import TeamGameStats
from hoops_sim.tui.theme import fg_pct_color
from hoops_sim.tui.widgets.quarter_scoring import QuarterScoringTable


class BoxScoreScreen(Screen):
    """Traditional + advanced box score from PlayerGameStats / TeamGameStats.

    Features:
    - Traditional stats view with FG% color coding
    - Highlight double-doubles/triple-doubles
    - Quarter-by-quarter scoring summary
    - Sortable columns
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
        home_quarters: list[int] | None = None,
        away_quarters: list[int] | None = None,
    ) -> None:
        super().__init__()
        self._home_stats = home_stats
        self._away_stats = away_stats
        self._home_name = home_name
        self._away_name = away_name
        self._home_quarters = home_quarters or []
        self._away_quarters = away_quarters or []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="box-score-screen"):
            home_total = sum(
                ps.points for ps in self._home_stats.player_stats.values()
            )
            away_total = sum(
                ps.points for ps in self._away_stats.player_stats.values()
            )
            yield Label(
                f"[bold]Box Score -- {self._away_name} {away_total} vs {self._home_name} {home_total}[/]",
                classes="screen-header",
            )
            yield Button("< Back", id="btn-back", classes="back-button")

            yield Label(
                f"\n[bold]{self._away_name}[/]", classes="conference-header"
            )
            away_table = DataTable(id="away-box-table")
            away_table.add_columns(
                "Player",
                "MIN",
                "PTS",
                "REB",
                "AST",
                "STL",
                "BLK",
                "FGM-A",
                "FG%",
                "3PM-A",
                "FTM-A",
                "TO",
                "+/-",
            )
            yield away_table

            yield Label(
                f"\n[bold]{self._home_name}[/]", classes="conference-header"
            )
            home_table = DataTable(id="home-box-table")
            home_table.add_columns(
                "Player",
                "MIN",
                "PTS",
                "REB",
                "AST",
                "STL",
                "BLK",
                "FGM-A",
                "FG%",
                "3PM-A",
                "FTM-A",
                "TO",
                "+/-",
            )
            yield home_table

            # Quarter scoring if available
            if self._home_quarters or self._away_quarters:
                yield Label("")
                yield QuarterScoringTable(
                    home_name=self._home_name,
                    away_name=self._away_name,
                    home_quarters=self._home_quarters,
                    away_quarters=self._away_quarters,
                    id="quarter-scoring",
                )
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
            pm_str = (
                f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            )

            # FG% with color coding
            fg_pct = ps.fgm / ps.fga if ps.fga > 0 else 0.0
            fg_color = fg_pct_color(fg_pct)
            fg_pct_str = f"[{fg_color}]{fg_pct:.3f}[/]" if ps.fga > 0 else "-"

            # Highlight notable performances
            name_str = ps.player_name[:18]
            if ps.is_triple_double():
                name_str = f"[bold #9b59b6]{name_str}[/]"
            elif ps.is_double_double():
                name_str = f"[bold]{name_str}[/]"

            table.add_row(
                name_str,
                f"{ps.minutes:.0f}",
                str(ps.points),
                str(ps.rebounds),
                str(ps.assists),
                str(ps.steals),
                str(ps.blocks),
                f"{ps.fgm}-{ps.fga}",
                fg_pct_str,
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
