"""Horizontal attribute bar 0-99 with color gradient."""

from __future__ import annotations

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import rating_color


class AttributeBar(Widget):
    """Horizontal bar displaying a 0-99 attribute rating with color gradient."""

    def __init__(
        self,
        label: str,
        value: int = 50,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._label = label
        self.value = max(0, min(99, value))

    def render(self) -> str:
        bar_width = self.value // 5
        color = rating_color(self.value)
        filled = "\u2588" * bar_width
        empty = "\u2591" * (20 - bar_width)
        return f"{self._label:<14} [{color}]{filled}[/]{empty} {self.value:>3}"

    def update_value(self, value: int) -> None:
        """Update the displayed value."""
        self.value = max(0, min(99, value))
