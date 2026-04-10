"""Scoring run sparkline widget.

Textual widget for displaying recent scoring runs.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


class ScoringRunSparkline(Widget):
    """Mini sparkline showing recent scoring runs."""

    def __init__(self, runs: list[int] | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._runs = runs or []

    def render(self) -> Text:
        text = Text()
        text.append("Run: ")
        if not self._runs:
            text.append("--", style="dim")
            return text
        blocks = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
        max_val = max(self._runs) if self._runs else 1
        for val in self._runs[-10:]:
            idx = int(val / max_val * 7) if max_val > 0 else 0
            idx = max(0, min(7, idx))
            text.append(blocks[idx])
        return text
