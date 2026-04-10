"""Mini schedule showing upcoming games.

Textual widget for the league hub's schedule preview.
"""

from __future__ import annotations

from typing import List, Tuple

from rich.text import Text
from textual.widget import Widget


class MiniSchedule(Widget):
    """Compact upcoming game schedule."""

    def __init__(
        self,
        games: List[Tuple[int, str, str]] | None = None,
        **kwargs,
    ) -> None:
        """Initialize with games as (day, ha_prefix, opponent_name)."""
        super().__init__(**kwargs)
        self._games = games or []

    def render(self) -> Text:
        text = Text()
        text.append("UPCOMING\n", style="bold")
        if not self._games:
            text.append("  No upcoming games", style="dim")
            return text
        for day, ha, opp in self._games[:5]:
            text.append(f"  Day {day:>3}: {ha} {opp}\n")
        return text
