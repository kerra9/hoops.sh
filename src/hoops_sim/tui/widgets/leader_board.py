"""Leader board widget showing top performers.

Textual widget for displaying stat leaders.
"""

from __future__ import annotations

from typing import List, Tuple

from rich.text import Text
from textual.widget import Widget


class LeaderBoard(Widget):
    """Compact leader board for stat categories."""

    def __init__(
        self,
        title: str = "LEADERS",
        leaders: List[Tuple[str, str, str]] | None = None,
        **kwargs,
    ) -> None:
        """Initialize with leaders as (stat, player_name, value)."""
        super().__init__(**kwargs)
        self._title = title
        self._leaders = leaders or []

    def render(self) -> Text:
        text = Text()
        text.append(f"{self._title}\n", style="bold")
        if not self._leaders:
            text.append("  No leaders yet", style="dim")
            return text
        for stat, name, value in self._leaders[:5]:
            text.append(f"  {stat:<6} {name:<16} {value}\n")
        return text
