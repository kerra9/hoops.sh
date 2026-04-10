"""Playoff picture strip widget.

Textual widget showing playoff seeding status.
"""

from __future__ import annotations

from typing import List

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import PLAYOFF_IN, PLAYOFF_OUT, PLAYOFF_PLAYIN


class PlayoffPictureStrip(Widget):
    """Playoff seeding status strip."""

    def __init__(
        self,
        east_teams: List[str] | None = None,
        west_teams: List[str] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._east = east_teams or []
        self._west = west_teams or []

    def render(self) -> Text:
        text = Text()
        text.append("EAST: ")
        for i, team in enumerate(self._east[:10]):
            if i < 6:
                color = PLAYOFF_IN
            elif i < 10:
                color = PLAYOFF_PLAYIN
            else:
                color = PLAYOFF_OUT
            text.append(f"{team} ", style=color)
        text.append("\nWEST: ")
        for i, team in enumerate(self._west[:10]):
            if i < 6:
                color = PLAYOFF_IN
            elif i < 10:
                color = PLAYOFF_PLAYIN
            else:
                color = PLAYOFF_OUT
            text.append(f"{team} ", style=color)
        return text
