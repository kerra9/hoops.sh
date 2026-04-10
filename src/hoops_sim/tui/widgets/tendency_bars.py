"""Tendency bars as horizontal progress indicators.

Textual widget for displaying player tendencies.
"""

from __future__ import annotations

from typing import Dict

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import ACCENT_PRIMARY


class TendencyBars(Widget):
    """Horizontal bars for player tendency/personality values."""

    def __init__(
        self,
        tendencies: Dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._tendencies = tendencies or {}

    def render(self) -> Text:
        text = Text()
        for name, value in self._tendencies.items():
            bar_len = 10
            filled = int(value / 100.0 * bar_len)
            filled = max(0, min(bar_len, filled))
            bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
            text.append(f"  {name:<14} ")
            text.append(bar, style=ACCENT_PRIMARY)
            text.append(f" {value:.0f}%\n")
        return text
