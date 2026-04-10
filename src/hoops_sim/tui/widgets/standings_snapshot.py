"""Compact top-5 standings snapshot widget."""

from __future__ import annotations

from typing import List, Tuple

from hoops_sim.tui.base import Widget


class StandingsSnapshot(Widget):
    """Compact top-5 standings display for a conference."""

    def __init__(
        self,
        conference: str = "",
        teams: List[Tuple[str, int, int, str]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with team tuples of (name, wins, losses, gb_str)."""
        super().__init__(name=name, id=id, classes=classes)
        self._conference = conference
        self._teams = teams or []

    def render(self) -> str:
        lines = [f"[bold]{self._conference}[/]{'':>5}W   L   GB"]
        for i, (team_name, wins, losses, gb) in enumerate(self._teams[:5], 1):
            lines.append(f"  {i}. {team_name:<12} {wins:>2}  {losses:>2}  {gb:>4}")
        if not self._teams:
            lines.append("  [dim]No standings data[/]")
        return "\n".join(lines)

    def update_standings(
        self, teams: List[Tuple[str, int, int, str]]
    ) -> None:
        """Update the standings snapshot."""
        self._teams = teams
