"""Sortable conference standings table from TeamRecord data."""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import DataTable

from hoops_sim.season.standings import TeamRecord


class StandingsTable(Widget):
    """Sortable conference standings table.

    Reads from a list of TeamRecord objects and renders
    a full standings display with W-L, PCT, GB, and streaks.
    """

    DEFAULT_CSS = """
    StandingsTable {
        height: auto;
        width: 100%;
    }
    """

    def __init__(
        self,
        records: List[TeamRecord] | None = None,
        conference: str = "",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._records = records or []
        self._conference = conference

    def compose(self) -> ComposeResult:
        table = DataTable(id=f"standings-{self._conference.lower()}")
        table.add_columns(
            "#", "Team", "W", "L", "PCT", "GB", "Home", "Away", "Conf", "Div", "Strk", "L10",
        )
        yield table

    def on_mount(self) -> None:
        self._populate()

    def _populate(self) -> None:
        table = self.query_one(DataTable)
        table.clear()

        # Sort by win pct descending
        sorted_records = sorted(self._records, key=lambda r: r.win_pct, reverse=True)
        leader_wins = sorted_records[0].wins if sorted_records else 0
        leader_losses = sorted_records[0].losses if sorted_records else 0

        for i, rec in enumerate(sorted_records, 1):
            gb = ((leader_wins - rec.wins) + (rec.losses - leader_losses)) / 2.0
            gb_str = "-" if gb == 0 else f"{gb:.1f}"
            streak_str = f"W{rec.streak}" if rec.streak > 0 else f"L{abs(rec.streak)}" if rec.streak < 0 else "-"
            table.add_row(
                str(i),
                rec.team_name,
                str(rec.wins),
                str(rec.losses),
                f"{rec.win_pct:.3f}",
                gb_str,
                f"{rec.home_wins}-{rec.home_losses}",
                f"{rec.away_wins}-{rec.away_losses}",
                f"{rec.conference_wins}-{rec.conference_losses}",
                f"{rec.division_wins}-{rec.division_losses}",
                streak_str,
                f"{rec.last_10_wins}-{rec.last_10_losses}",
            )

    def update_records(self, records: List[TeamRecord]) -> None:
        """Update the standings with new records."""
        self._records = records
        self._populate()
