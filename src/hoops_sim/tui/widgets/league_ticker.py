"""League ticker showing recent game results.

Textual widget for the league hub's results ticker.
"""

from __future__ import annotations

from typing import List, Tuple

from rich.text import Text
from textual.widget import Widget


class LeagueTicker(Widget):
    """Scrolling ticker of recent game results."""

    def __init__(
        self,
        results: List[Tuple[str, int, str, int]] | None = None,
        **kwargs,
    ) -> None:
        """Initialize with results as (away_name, away_score, home_name, home_score)."""
        super().__init__(**kwargs)
        self._results = results or []

    def render(self) -> Text:
        text = Text()
        text.append("RECENT RESULTS\n", style="bold")
        if not self._results:
            text.append("  No games played yet", style="dim")
            return text
        for away, a_score, home, h_score in self._results[:5]:
            text.append(f"  {away} {a_score} @ {home} {h_score}\n")
        return text
