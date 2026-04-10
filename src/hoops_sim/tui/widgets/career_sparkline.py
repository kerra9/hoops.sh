"""Career sparkline widget placeholder.

Textual widget for showing career stat trends.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class CareerSparkline(Widget):
    """Career stats sparkline."""

    def __init__(self, values: list[float] | None = None, label: str = "", **kwargs) -> None:
        super().__init__(**kwargs)
        self._values = values or []
        self._label = label

    def render(self) -> Text:
        text = Text()
        text.append(f"{self._label}: ")
        if not self._values:
            text.append("--", style="dim")
            return text
        blocks = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
        max_val = max(self._values) if self._values else 1
        for val in self._values:
            idx = int(val / max_val * 7) if max_val > 0 else 0
            idx = max(0, min(7, idx))
            text.append(blocks[idx])
        return text
