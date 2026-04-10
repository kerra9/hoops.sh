"""Scoring run sparkline for visualizing momentum shifts."""

from __future__ import annotations

from typing import List

from hoops_sim.tui.base import Widget
from hoops_sim.tui.widgets.career_sparkline import sparkline


class ScoringRunSparkline(Widget):
    """Sparkline showing scoring run trends during a game."""

    def __init__(
        self,
        label: str = "Scoring Runs",
        runs: List[float] | None = None,
        color: str = "#ffd700",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._label = label
        self._runs = runs or []
        self._color = color

    def render(self) -> str:
        spark = sparkline(self._runs)
        return f"{self._label}: [{self._color}]{spark}[/]"

    def update_runs(self, runs: List[float]) -> None:
        """Update the scoring run data."""
        self._runs = runs
