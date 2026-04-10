"""Attribute radar/spider chart using text-based visualization.

Textual widget for displaying player attribute categories as bars.
"""

from __future__ import annotations

from typing import Dict

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import rating_color


class AttributeRadar(Widget):
    """Attribute category overview as horizontal bars.

    Displays each attribute category (Shooting, Finishing, etc.)
    as a labeled bar with color based on rating value.
    """

    def __init__(
        self,
        categories: Dict[str, float] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._categories = categories or {}

    def render(self) -> Text:
        text = Text()
        for name, value in self._categories.items():
            int_val = int(value)
            bar_len = 10
            filled = int(int_val / 99 * bar_len)
            filled = max(0, min(bar_len, filled))
            color = rating_color(int_val)
            bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
            text.append(f"  {name:<14} ")
            text.append(bar, style=color)
            text.append(f" {int_val:>2}\n")
        return text
