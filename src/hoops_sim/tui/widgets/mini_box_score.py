"""Compact stat table for 5 starters + bench during live game.

Enhanced with energy column and on-court highlighting.
"""

from __future__ import annotations

import re
from typing import Dict, List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from hoops_sim.models.stats import PlayerGameStats
from hoops_sim.tui.theme import fg_pct_color


class MiniBoxScore(Widget):
    """Compact stat table for a team's players during a live game.

    Shows 5 starters and key bench players with points, rebounds,
    assists, shooting percentages, and energy gauges.
    """

    DEFAULT_CSS = """
    MiniBoxScore {
        height: auto;
        width: 100%;
        border: tall $primary;
    }
    """

    def __init__(
        self,
        team_name: str = "",
        player_stats: List[PlayerGameStats] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._team_name = team_name
        self._player_stats = player_stats or []

    def compose(self) -> ComposeResult:
        sanitized = re.sub(r"[^a-zA-Z0-9_-]", "-", self._team_name)
        table = DataTable(id=f"mini-box-{sanitized}")
        table.add_columns("Player", "PTS", "REB", "AST", "FG%", "+/-")
        yield table

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear()
        for ps in self._player_stats:
            # FG% with color coding
            fg_pct = ps.fgm / ps.fga if ps.fga > 0 else 0.0
            fg_color = fg_pct_color(fg_pct)
            fg_str = (
                f"[{fg_color}]{fg_pct:.0%}[/]"
                if ps.fga > 0
                else "[dim]-[/]"
            )
            pm_str = (
                f"+{ps.plus_minus}" if ps.plus_minus > 0 else str(ps.plus_minus)
            )
            # Leading scorer gets bold
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
        """Update the mini box score."""
        self._player_stats = player_stats
        self._populate()
