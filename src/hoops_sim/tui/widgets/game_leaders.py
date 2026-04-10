"""Top performers grid for post-game display.

Textual widget using Rich Text for colored stat leader display.
"""

from __future__ import annotations

from typing import List, Tuple

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import SCORE_GOLD


class GameLeadersPanel(Widget):
    """Game leaders panel showing top performers by stat category."""

    def __init__(
        self,
        leaders: List[Tuple[str, str, str]] | None = None,
        **kwargs,
    ) -> None:
        """Initialize with leader tuples of (stat_abbr, player_name, value)."""
        super().__init__(**kwargs)
        self._leaders = leaders or []

    def render(self) -> Text:
        text = Text()
        text.append("GAME LEADERS\n", style="bold")
        pairs = list(zip(self._leaders[::2], self._leaders[1::2]))
        for left, right in pairs:
            l_stat, l_name, l_val = left
            r_stat, r_name, r_val = right
            text.append(f"  {l_stat}", style=SCORE_GOLD)
            text.append(f": {l_name} {l_val}")
            text.append(f"    | {r_stat}", style=SCORE_GOLD)
            text.append(f": {r_name} {r_val}\n")
        if len(self._leaders) % 2 == 1:
            stat, player_name, val = self._leaders[-1]
            text.append(f"  {stat}", style=SCORE_GOLD)
            text.append(f": {player_name} {val}\n")
        return text
