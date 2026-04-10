"""Compact playoff seeding strip."""

from __future__ import annotations

from typing import List, Tuple

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import PLAYOFF_IN, PLAYOFF_OUT, PLAYOFF_PLAYIN


class PlayoffPictureStrip(Widget):
    """Compact playoff seeding strip showing teams in/out.

    Seeds 1-8 in green, 9-10 play-in yellow, rest red.
    """

    DEFAULT_CSS = """
    PlayoffPictureStrip {
        height: 2;
        width: 100%;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        east_teams: List[str] | None = None,
        west_teams: List[str] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with lists of team abbreviations sorted by seed."""
        super().__init__(name=name, id=id, classes=classes)
        self._east = east_teams or []
        self._west = west_teams or []

    def _format_conf(self, label: str, teams: List[str]) -> str:
        """Format one conference line."""
        parts = [f"{label}: "]
        for i, team in enumerate(teams):
            if i < 8:
                parts.append(f"[{PLAYOFF_IN}]{team}[/] ")
            elif i < 10:
                parts.append(f"[{PLAYOFF_PLAYIN}]{team}[/] ")
            else:
                parts.append(f"[{PLAYOFF_OUT}]{team}[/] ")
            if i == 7:
                parts.append("| ")
        return "".join(parts)

    def compose(self) -> ComposeResult:
        yield Label(self._format_conf("E", self._east))
        yield Label(self._format_conf("W", self._west))

    def update_picture(
        self, east_teams: List[str], west_teams: List[str]
    ) -> None:
        """Update the playoff picture."""
        self._east = east_teams
        self._west = west_teams
        self.refresh(recompose=True)
