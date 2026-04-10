"""Position-based depth chart visualization."""

from __future__ import annotations

from typing import Dict, List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import ACCENT_SUCCESS

POSITIONS = ["PG", "SG", "SF", "PF", "C"]


class DepthChart(Widget):
    """Position-based depth chart showing starters and backups.

    Shows each position with starter and backup names.
    """

    DEFAULT_CSS = """
    DepthChart {
        height: auto;
        width: 100%;
        padding: 0;
    }
    """

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

    def compose(self) -> ComposeResult:
        yield Label("[bold]DEPTH CHART[/]")
        with Vertical():
            for pos in POSITIONS:
                players = self._depth.get(pos, [])
                players_str = " / ".join(players) if players else "[dim]--[/]"
                yield Label(f"  [{ACCENT_SUCCESS}]{pos}:[/] {players_str}")

    def update_depth(self, depth: Dict[str, List[str]]) -> None:
        """Update the depth chart."""
        self._depth = depth
        self.refresh(recompose=True)
