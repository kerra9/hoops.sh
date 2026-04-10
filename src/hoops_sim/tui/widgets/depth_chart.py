"""Position-based depth chart visualization."""

from __future__ import annotations

from typing import Dict, List

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import ACCENT_SUCCESS

POSITIONS = ["PG", "SG", "SF", "PF", "C"]


class DepthChart(Widget):
    """Position-based depth chart showing starters and backups."""

    def __init__(
        self,
        depth: Dict[str, List[str]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with depth dict of {position: [player_names]}."""
        super().__init__(name=name, id=id, classes=classes)
        self._depth = depth or {}

    def render(self) -> str:
        lines = ["[bold]DEPTH CHART[/]"]
        for pos in POSITIONS:
            players = self._depth.get(pos, [])
            players_str = " / ".join(players) if players else "[dim]--[/]"
            lines.append(f"  [{ACCENT_SUCCESS}]{pos}:[/] {players_str}")
        return "\n".join(lines)

    def update_depth(self, depth: Dict[str, List[str]]) -> None:
        """Update the depth chart."""
        self._depth = depth
