"""Game flow sparkline showing scoring momentum over time."""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.widgets.career_sparkline import sparkline


class ScoringRunSparkline(Widget):
    """Game flow sparkline showing scoring run momentum.

    Displays scoring rate over time as a braille sparkline.
    """

    DEFAULT_CSS = """
    ScoringRunSparkline {
        height: 1;
        width: 100%;
    }
    """

    def __init__(
        self,
        label: str = "",
        values: List[float] | None = None,
        color: str = "#3498db",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._label = label
        self._values = values or []
        self._color = color

    def compose(self) -> ComposeResult:
        spark = sparkline(self._values, width=30)
        yield Label(f"{self._label}: [{self._color}]{spark}[/]")

    def update_values(self, values: List[float]) -> None:
        """Update the sparkline data."""
        self._values = values
        self.refresh(recompose=True)
