"""Sortable conference standings table from TeamRecord data.

Textual widget using DataTable for sortable, scrollable standings.
"""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from hoops_sim.season.standings import TeamRecord


class StandingsTableWidget(Widget):
    """Sortable conference standings table using Textual DataTable.

    Reads from a list of TeamRecord objects and renders
    a full standings display with W-L, PCT, GB, and streaks.
    """

    def __init__(
        self,
        records: List[TeamRecord] | None = None,
        conference: str = "",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._records = records or []
        self._conference = conference

    def compose(self) -> ComposeResult:
        table = DataTable(id="standings-dt")
        table.add_columns("#", "Team", "W", "L", "PCT", "GB", "Strk")
        yield table

    def on_mount(self) -> None:
        self._refresh_table()

    def _refresh_table(self) -> None:
        table = self.query_one("#standings-dt", DataTable)
        table.clear()

        sorted_records = sorted(self._records, key=lambda r: r.win_pct, reverse=True)
        leader_wins = sorted_records[0].wins if sorted_records else 0
        leader_losses = sorted_records[0].losses if sorted_records else 0

        for i, rec in enumerate(sorted_records, 1):
            gb = ((leader_wins - rec.wins) + (rec.losses - leader_losses)) / 2.0
            gb_str = "-" if gb == 0 else f"{gb:.1f}"
            streak_str = (
                f"W{rec.streak}"
                if rec.streak > 0
                else f"L{abs(rec.streak)}"
                if rec.streak < 0
                else "-"
            )
            table.add_row(
                str(i),
                rec.team_name[:16],
                str(rec.wins),
                str(rec.losses),
                f"{rec.win_pct:.3f}",
                gb_str,
                streak_str,
            )

    def update_records(self, records: List[TeamRecord]) -> None:
        """Update standings with new records."""
        self._records = records
        try:
            self._refresh_table()
        except Exception:
            pass


# Backward-compatible alias
StandingsTable = StandingsTableWidget
