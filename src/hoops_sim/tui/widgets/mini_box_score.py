"""Compact stat table for 5 starters + bench during live game.

Textual widget using DataTable for sortable, scrollable stats.
"""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable, Static

from hoops_sim.models.stats import PlayerGameStats
from hoops_sim.tui.theme import fg_pct_color


class MiniBoxScoreWidget(Widget):
    """Compact stat table for a team's players during a live game.

    Uses Textual DataTable for sortable columns and proper scrolling.
    """

    def __init__(
        self,
        team_name: str = "",
        player_stats: List[PlayerGameStats] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._team_name = team_name
        self._player_stats = player_stats or []

    def compose(self) -> ComposeResult:
        yield Static(self._team_name, classes="section-title")
        table = DataTable(id="mini-box-table")
        table.add_columns("Player", "PTS", "REB", "AST", "FG%", "+/-")
        yield table

    def on_mount(self) -> None:
        self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one("#mini-box-table", DataTable)
        table.clear()
        for ps in self._player_stats:
            fg_pct = ps.fgm / ps.fga if ps.fga > 0 else 0.0
            fg_str = f"{fg_pct:.0%}" if ps.fga > 0 else "-"
            pm_str = f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            name_str = ps.player_name[:15]
            table.add_row(
                name_str,
                str(ps.points),
                str(ps.rebounds),
                str(ps.assists),
                fg_str,
                pm_str,
            )

    def update_stats(self, player_stats: List[PlayerGameStats]) -> None:
        """Update the mini box score with new stats."""
        self._player_stats = player_stats
        try:
            self._refresh_table()
        except Exception:
            pass


# Keep backward-compatible alias
MiniBoxScore = MiniBoxScoreWidget
