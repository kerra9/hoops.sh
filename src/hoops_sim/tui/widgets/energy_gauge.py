"""Energy gauge using ProgressBar with color tiers.

Textual widget for displaying player energy levels.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import energy_color


class EnergyGauge(Widget):
    """Energy bar with color that changes based on fatigue tier."""

    def __init__(
        self,
        value: float = 1.0,
        label: str = "Energy",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._value = max(0.0, min(1.0, value))
        self._label = label

    def render(self) -> Text:
        bar_len = 10
        filled = int(self._value * bar_len)
        color = energy_color(self._value)
        bar = "\u2588" * filled + "\u2591" * (bar_len - filled)

        text = Text()
        text.append(f"{self._label:<10} ")
        text.append(bar, style=color)
        text.append(f" {self._value:.0%}")
        return text

    def update_value(self, value: float) -> None:
        self._value = max(0.0, min(1.0, value))
        self.refresh()
