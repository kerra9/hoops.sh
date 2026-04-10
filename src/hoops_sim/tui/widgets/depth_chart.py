"""Depth chart display widget.

Textual widget for showing team depth chart by position.
"""

from __future__ import annotations

from typing import Dict, List

from rich.text import Text
from textual.widget import Widget


class DepthChart(Widget):
    """Depth chart showing starters and backups by position."""

    def __init__(
        self,
        depth: Dict[str, List[str]] | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._depth = depth or {}

    def render(self) -> Text:
        text = Text()
        text.append("DEPTH CHART\n", style="bold")
        for pos in ["PG", "SG", "SF", "PF", "C"]:
            players = self._depth.get(pos, [])
            names = ", ".join(players) if players else "-"
            text.append(f"  {pos}: ", style="bold")
            text.append(f"{names}\n")
        return text
