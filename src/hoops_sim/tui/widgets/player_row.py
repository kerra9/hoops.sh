"""Player row widget for roster displays.

Textual widget for a single player row in a roster list.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import energy_color, rating_color


class PlayerRow(Widget):
    """Single player row for roster display."""

    def __init__(
        self,
        jersey: int = 0,
        name: str = "",
        position: str = "",
        age: int = 0,
        overall: int = 0,
        height_str: str = "",
        energy_pct: float = 1.0,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._jersey = jersey
        self._name = name
        self._position = position
        self._age = age
        self._overall = overall
        self._height_str = height_str
        self._energy_pct = energy_pct

    def render(self) -> Text:
        ovr_color = rating_color(self._overall)
        e_color = energy_color(self._energy_pct)
        e_bar = int(self._energy_pct * 5)
        e_filled = "\u2588" * e_bar
        e_empty = "\u2591" * (5 - e_bar)

        text = Text()
        text.append(f"{self._jersey:>3} {self._name:<22} {self._position:<4} {self._age:>3} ")
        text.append(f"{self._overall:>3}", style=ovr_color)
        text.append(f" {self._height_str:>6}  ")
        text.append(f"{e_filled}{e_empty}", style=e_color)
        return text
