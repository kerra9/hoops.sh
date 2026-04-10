"""Quarter-by-quarter scoring breakdown.

Textual widget for displaying scoring by quarter.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class QuarterScoringTable(Widget):
    """Quarter scoring summary."""

    def __init__(
        self,
        home_name: str = "Home",
        away_name: str = "Away",
        home_quarters: list[int] | None = None,
        away_quarters: list[int] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._home_name = home_name
        self._away_name = away_name
        self._home_quarters = home_quarters or []
        self._away_quarters = away_quarters or []

    def render(self) -> Text:
        text = Text()
        num_q = max(len(self._home_quarters), len(self._away_quarters), 4)

        # Header
        text.append(f"{'Team':<16}", style="bold")
        for i in range(num_q):
            label = f"Q{i + 1}" if i < 4 else f"OT{i - 3}"
            text.append(f" {label:>4}")
        text.append(f" {'TOT':>4}\n", style="bold")

        # Away
        text.append(f"{self._away_name:<16}")
        for i in range(num_q):
            val = self._away_quarters[i] if i < len(self._away_quarters) else 0
            text.append(f" {val:>4}")
        text.append(f" {sum(self._away_quarters):>4}\n")

        # Home
        text.append(f"{self._home_name:<16}")
        for i in range(num_q):
            val = self._home_quarters[i] if i < len(self._home_quarters) else 0
            text.append(f" {val:>4}")
        text.append(f" {sum(self._home_quarters):>4}")
        return text
