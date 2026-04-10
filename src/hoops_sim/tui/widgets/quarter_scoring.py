"""Quarter-by-quarter scoring breakdown table."""

from __future__ import annotations

from typing import Dict, List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class QuarterScoringTable(Widget):
    """Quarter-by-quarter scoring breakdown.

    Shows Q1-Q4 + OT + Total for both teams.
    """

    DEFAULT_CSS = """
    QuarterScoringTable {
        height: auto;
        width: 100%;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        home_quarters: List[int] | None = None,
        away_quarters: List[int] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._home_name = home_name
        self._away_name = away_name
        self._home_q = home_quarters or [0, 0, 0, 0]
        self._away_q = away_quarters or [0, 0, 0, 0]

    def compose(self) -> ComposeResult:
        yield Label("[bold]QUARTER SCORING[/]")
        # Header
        q_headers = "  ".join(f"Q{i+1}" for i in range(len(self._home_q)))
        home_total = sum(self._home_q)
        away_total = sum(self._away_q)
        yield Label(f"  {'':>12}  {q_headers}  TOTAL")

        away_scores = "  ".join(f"{q:>2}" for q in self._away_q)
        yield Label(f"  {self._away_name:>12}  {away_scores}  {away_total:>5}")

        home_scores = "  ".join(f"{q:>2}" for q in self._home_q)
        yield Label(f"  {self._home_name:>12}  {home_scores}  {home_total:>5}")
