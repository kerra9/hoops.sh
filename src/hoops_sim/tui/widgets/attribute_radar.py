"""Text-based radar/spider chart for the 7 attribute categories."""

from __future__ import annotations

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import rating_color


class AttributeRadar(Widget):
    """Text-based display of all 7 attribute category averages.

    Shows a horizontal bar chart summarizing each category with
    color gradient based on rating value.
    """

    def __init__(
        self,
        categories: dict[str, int] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._categories = categories or {}

    def render(self) -> str:
        lines = []
        for cat_name, value in self._categories.items():
            bar_w = value // 5
            color = rating_color(value)
            filled = "\u2588" * bar_w
            empty = "\u2591" * (20 - bar_w)
            lines.append(f"{cat_name:<14} [{color}]{filled}[/]{empty} {value:>3}")
        return "\n".join(lines)

    def update_categories(self, categories: dict[str, int]) -> None:
        """Update the radar chart data."""
        self._categories = categories
