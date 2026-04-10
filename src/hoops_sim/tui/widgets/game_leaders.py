"""Top performers grid for post-game display."""

from __future__ import annotations

from typing import List, Tuple

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import SCORE_GOLD


class GameLeadersPanel(Widget):
    """Game leaders panel showing top performers by stat category.

    Displays PTS, REB, AST, STL, BLK, 3PM leaders.
    """

    DEFAULT_CSS = """
    GameLeadersPanel {
        height: auto;
        width: 100%;
        padding: 1;
    }
    """

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

    def compose(self) -> ComposeResult:
        yield Label("[bold]GAME LEADERS[/]")
        with Vertical():
            # Display in 2 columns by pairing leaders
            pairs = list(zip(self._leaders[::2], self._leaders[1::2]))
            for left, right in pairs:
                l_stat, l_name, l_val = left
                r_stat, r_name, r_val = right
                yield Label(
                    f"  [{SCORE_GOLD}]{l_stat}[/]: {l_name} {l_val}"
                    f"    | [{SCORE_GOLD}]{r_stat}[/]: {r_name} {r_val}"
                )
            # Handle odd leader
            if len(self._leaders) % 2 == 1:
                stat, player_name, val = self._leaders[-1]
                yield Label(f"  [{SCORE_GOLD}]{stat}[/]: {player_name} {val}")
