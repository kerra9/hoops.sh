"""Salary cap visualization widget.

Textual widget for displaying team salary cap status.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import SCORE_GREEN, SCORE_RED, ACCENT_WARNING


class SalaryCapBar(Widget):
    """Salary cap bar showing payroll vs cap."""

    def __init__(
        self,
        payroll: float = 0.0,
        cap_info=None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._payroll = payroll
        self._cap_info = cap_info

    def render(self) -> Text:
        text = Text()
        text.append("SALARY CAP\n", style="bold")

        cap = 140_000_000.0
        if self._cap_info and hasattr(self._cap_info, "cap"):
            cap = self._cap_info.cap

        pct = self._payroll / cap if cap > 0 else 0.0
        bar_len = 20
        filled = int(pct * bar_len)
        filled = max(0, min(bar_len, filled))

        if pct > 1.0:
            color = SCORE_RED
        elif pct > 0.85:
            color = ACCENT_WARNING
        else:
            color = SCORE_GREEN

        bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
        text.append(f"  ")
        text.append(bar, style=color)
        text.append(f" ${self._payroll / 1_000_000:.1f}M / ${cap / 1_000_000:.0f}M")
        return text
