"""Top performers grid for post-game display."""

from __future__ import annotations

from typing import List, Tuple

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import SCORE_GOLD


class GameLeadersPanel(Widget):
    """Game leaders panel showing top performers by stat category."""

    def __init__(
        self,
        leaders: List[Tuple[str, str, str]] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with leader tuples of (stat_abbr, player_name, value)."""
        super().__init__(name=name, id=id, classes=classes)
        self._leaders = leaders or []

    def render(self) -> str:
        lines = ["[bold]GAME LEADERS[/]"]
        pairs = list(zip(self._leaders[::2], self._leaders[1::2]))
        for left, right in pairs:
            l_stat, l_name, l_val = left
            r_stat, r_name, r_val = right
            lines.append(
                f"  [{SCORE_GOLD}]{l_stat}[/]: {l_name} {l_val}"
                f"    | [{SCORE_GOLD}]{r_stat}[/]: {r_name} {r_val}"
            )
        if len(self._leaders) % 2 == 1:
            stat, player_name, val = self._leaders[-1]
            lines.append(f"  [{SCORE_GOLD}]{stat}[/]: {player_name} {val}")
        return "\n".join(lines)
