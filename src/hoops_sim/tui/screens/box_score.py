"""Box Score screen -- tabbed traditional + advanced stats.

Textual Screen with DataTable widgets for sortable, scrollable stats.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import DataTable, Footer, Header, Static

from hoops_sim.models.stats import TeamGameStats
from hoops_sim.tui.theme import fg_pct_color
from hoops_sim.tui.widgets.quarter_scoring import QuarterScoringTable


class BoxScoreScreen(Screen):
    """Traditional + advanced box score from PlayerGameStats / TeamGameStats.

    Uses DataTable widgets for sortable columns and proper scrolling.
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("b", "go_back", "Back"),
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
        home_total = sum(ps.points for ps in self._home_stats.player_stats.values())
        away_total = sum(ps.points for ps in self._away_stats.player_stats.values())

        yield Header()
        with VerticalScroll(id="box-score"):
            yield Static(
                f"[bold]Box Score -- {self._away_name} {away_total} vs "
                f"{self._home_name} {home_total}[/]",
                markup=True,
            )

            yield Static(f"\n[bold]{self._away_name}[/]", markup=True)
            yield self._build_table(self._away_stats, "away-table")

            yield Static(f"\n[bold]{self._home_name}[/]", markup=True)
            yield self._build_table(self._home_stats, "home-table")

            if self._home_quarters or self._away_quarters:
                yield QuarterScoringTable(
                    home_name=self._home_name,
                    away_name=self._away_name,
                    home_quarters=self._home_quarters,
                    away_quarters=self._away_quarters,
                )
        yield Footer()

    def _build_table(self, team_stats: TeamGameStats, table_id: str) -> DataTable:
        table = DataTable(id=table_id, classes="box-score-table")
        table.add_columns(
            "Player", "MIN", "PTS", "REB", "AST", "STL", "BLK",
            "FGM-A", "FG%", "3PM-A", "FTM-A", "TO", "+/-",
        )
        for ps in sorted(
            team_stats.player_stats.values(),
            key=lambda s: s.minutes,
            reverse=True,
        ):
            pm_str = f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            fg_pct = ps.fgm / ps.fga if ps.fga > 0 else 0.0
            fg_pct_str = f"{fg_pct:.3f}" if ps.fga > 0 else "-"
            name_str = ps.player_name[:18]

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
        return table

    def action_go_back(self) -> None:
        self.app.pop_screen()
