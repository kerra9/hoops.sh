"""Team stats summary panel.

Textual widget for displaying team aggregate statistics.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class TeamStatsPanel(Widget):
    """Team stats summary panel."""

    def __init__(self, stats=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._stats = stats

    def render(self) -> Text:
        text = Text()
        text.append("TEAM STATS\n", style="bold")
        if not self._stats:
            text.append("  No stats available yet", style="dim")
        return text
