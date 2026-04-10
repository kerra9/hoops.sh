"""Shot/play tendency frequency bars."""

from __future__ import annotations

from typing import Dict

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import ACCENT_PRIMARY


class TendencyBars(Widget):
    """Horizontal frequency bars for shot/play tendencies.

    Shows each tendency as a labeled bar with percentage.
    """

    DEFAULT_CSS = """
    TendencyBars {
        height: auto;
        width: 100%;
        padding: 0;
    }
    """

    def __init__(
        self,
        tendencies: Dict[str, float] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        """Initialize with tendency dict of {name: percentage (0-100)}."""
        super().__init__(name=name, id=id, classes=classes)
        self._tendencies = tendencies or {}

    def compose(self) -> ComposeResult:
        with Vertical():
            for tend_name, pct in self._tendencies.items():
                bar_w = int(pct / 100.0 * 10)
                filled = "\u2588" * bar_w
                empty = "\u2591" * (10 - bar_w)
                yield Label(
                    f"{tend_name:<14} [{ACCENT_PRIMARY}]{filled}[/]{empty} {pct:.0f}%"
                )

    def update_tendencies(self, tendencies: Dict[str, float]) -> None:
        """Update tendency data."""
        self._tendencies = tendencies
        self.refresh(recompose=True)
