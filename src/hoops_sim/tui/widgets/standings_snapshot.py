"""Compact standings snapshot for the league hub.

Textual widget for displaying top 5 teams in a conference.
"""

from __future__ import annotations

from typing import List, Tuple

from rich.text import Text
from textual.widget import Widget


class StandingsSnapshot(Widget):
    """Compact standings snapshot showing top 5 teams."""

    def __init__(
        self,
        conference: str = "",
        teams: List[Tuple[str, int, int, str]] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._conference = conference
        self._teams = teams or []

    def render(self) -> Text:
        text = Text()
        text.append(f"{self._conference} Conference\n", style="bold")
        text.append(f"  {'Team':<12} {'W':>3} {'L':>3} {'GB':>5}\n", style="dim")
        for name, wins, losses, gb in self._teams:
            text.append(f"  {name:<12} {wins:>3} {losses:>3} {gb:>5}\n")
        return text
