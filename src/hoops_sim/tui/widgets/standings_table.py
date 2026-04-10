"""Sortable conference standings table from TeamRecord data."""

from __future__ import annotations

from typing import List

from hoops_sim.season.standings import TeamRecord
from hoops_sim.tui.base import Widget


class StandingsTable(Widget):
    """Sortable conference standings table.

    Reads from a list of TeamRecord objects and renders
    a full standings display with W-L, PCT, GB, and streaks.
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

    def render(self) -> str:
        lines = []
        header = (
            f"{'#':>2} {'Team':<16} {'W':>3} {'L':>3} {'PCT':>6} {'GB':>5} "
            f"{'Home':>6} {'Away':>6} {'Conf':>6} {'Div':>5} {'Strk':>5} {'L10':>5}"
        )
        lines.append(header)

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
            lines.append(
                f"{i:>2} {rec.team_name:<16} {rec.wins:>3} {rec.losses:>3} "
                f"{rec.win_pct:>6.3f} {gb_str:>5} "
                f"{rec.home_wins}-{rec.home_losses:>5} "
                f"{rec.away_wins}-{rec.away_losses:>5} "
                f"{rec.conference_wins}-{rec.conference_losses:>5} "
                f"{rec.division_wins}-{rec.division_losses:>4} "
                f"{streak_str:>5} "
                f"{rec.last_10_wins}-{rec.last_10_losses:>4}"
            )
        return "\n".join(lines)

    def update_records(self, records: List[TeamRecord]) -> None:
        """Update the standings with new records."""
        self._records = records
