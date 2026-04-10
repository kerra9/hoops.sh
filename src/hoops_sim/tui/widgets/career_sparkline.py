"""Braille-character sparkline for career stat trends."""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

# Braille/block sparkline characters (8 levels)
_SPARK_CHARS = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"


def sparkline(values: List[float], width: int = 20) -> str:
    """Generate a sparkline string from a list of float values.

    Returns a string of block characters representing the trend.
    """
    if not values:
        return ""

    # Resample to fit width if needed
    if len(values) > width:
        step = len(values) / width
        sampled = [values[int(i * step)] for i in range(width)]
    else:
        sampled = values

    min_val = min(sampled)
    max_val = max(sampled)
    val_range = max_val - min_val if max_val != min_val else 1.0

    result = []
    for v in sampled:
        idx = int((v - min_val) / val_range * 7)
        idx = max(0, min(7, idx))
        result.append(_SPARK_CHARS[idx])
    return "".join(result)


class CareerSparkline(Widget):
    """Compact braille-character sparkline for career stat trends.

    Shows a single-line sparkline with a label prefix.
    """

    DEFAULT_CSS = """
    CareerSparkline {
        height: 1;
        width: 100%;
    }
    """

    def __init__(
        self,
        label: str = "",
        values: List[float] | None = None,
        color: str = "#2ecc71",
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
        spark = sparkline(self._values)
        yield Label(f"{self._label}: [{self._color}]{spark}[/]")

    def update_values(self, values: List[float]) -> None:
        """Update the sparkline data."""
        self._values = values
        self.refresh(recompose=True)
