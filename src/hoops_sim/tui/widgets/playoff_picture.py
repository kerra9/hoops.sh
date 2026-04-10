"""Compact playoff seeding strip."""

from __future__ import annotations

from typing import List

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import PLAYOFF_IN, PLAYOFF_OUT, PLAYOFF_PLAYIN


class PlayoffPictureStrip(Widget):
    """Compact playoff seeding strip showing teams in/out.

    Seeds 1-8 in green, 9-10 play-in yellow, rest red.
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

    def render(self) -> str:
        return (
            self._format_conf("E", self._east) + "\n"
            + self._format_conf("W", self._west)
        )

    def update_picture(
        self, east_teams: List[str], west_teams: List[str]
    ) -> None:
        """Update the playoff picture."""
        self._east = east_teams
        self._west = west_teams
