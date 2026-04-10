"""Stat leader display widget."""

from __future__ import annotations

from typing import List, Tuple

from hoops_sim.tui.base import Widget


class LeaderBoard(Widget):
    """Stat leader display showing top performers in a category."""

    def __init__(
        self,
        title: str = "LEADERS",
        leaders: List[Tuple[str, str, str]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with leader tuples of (stat_abbr, player_name, value_str)."""
        super().__init__(name=name, id=id, classes=classes)
        self._title = title
        self._leaders = leaders or []

    def render(self) -> str:
        lines = [f"[bold]{self._title}[/]"]
        for stat, player, value in self._leaders:
            lines.append(f"  {stat}: {player} {value}")
        if not self._leaders:
            lines.append("  [dim]No stats yet[/]")
        return "\n".join(lines)

    def update_leaders(self, leaders: List[Tuple[str, str, str]]) -> None:
        """Update the leader board."""
        self._leaders = leaders
