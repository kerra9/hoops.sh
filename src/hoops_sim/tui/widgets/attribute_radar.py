"""Text-based radar/spider chart for the 7 attribute categories."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.widgets.attribute_bar import _rating_color


class AttributeRadar(Widget):
    """Text-based display of all 7 attribute category averages.

    Shows a horizontal bar chart summarizing each category:
    Shooting, Finishing, Playmaking, Defense, Rebounding, Athleticism, Mental.
    """

    DEFAULT_CSS = """
    AttributeRadar {
        height: auto;
        width: 100%;
        padding: 1;
    }
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

    def compose(self) -> ComposeResult:
        with Vertical():
            for cat_name, value in self._categories.items():
                bar_w = value // 5
                color = _rating_color(value)
                filled = "\u2588" * bar_w
                empty = "\u2591" * (20 - bar_w)
                yield Label(
                    f"{cat_name:<14} [{color}]{filled}[/]{empty} {value:>3}"
                )

    def update_categories(self, categories: dict[str, int]) -> None:
        """Update the radar chart data."""
        self._categories = categories
        self.refresh(recompose=True)
