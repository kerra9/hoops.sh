"""Season progress bar widget.

Textual widget for showing season completion percentage.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import ACCENT_PRIMARY


class SeasonProgressBar(Widget):
    """Season progress bar."""

    def __init__(
        self,
        games_played: int = 0,
        total_games: int = 82,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._played = games_played
        self._total = total_games

    def render(self) -> Text:
        pct = self._played / self._total if self._total > 0 else 0.0
        bar_len = 20
        filled = int(pct * bar_len)
        bar = "\u2588" * filled + "\u2591" * (bar_len - filled)

        text = Text()
        text.append("Season Progress  ")
        text.append(bar, style=ACCENT_PRIMARY)
        text.append(f"  {self._played}/{self._total} ({pct:.0%})")
        return text
