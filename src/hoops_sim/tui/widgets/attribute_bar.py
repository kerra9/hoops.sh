"""Horizontal attribute bar using Unicode block characters.

Textual widget for displaying player attribute values.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import rating_color


class AttributeBar(Widget):
    """Horizontal bar using Unicode block characters with color gradient."""

    def __init__(
        self,
        label: str = "",
        value: int = 0,
        max_value: int = 99,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._label = label
        self._value = value
        self._max_value = max_value

    def render(self) -> Text:
        bar_len = 10
        filled = int(self._value / self._max_value * bar_len)
        filled = max(0, min(bar_len, filled))
        color = rating_color(self._value)
        bar = "\u2588" * filled + "\u2591" * (bar_len - filled)

        text = Text()
        text.append(f"{self._label:<14} ")
        text.append(bar, style=color)
        text.append(f" {self._value:>2}")
        return text
