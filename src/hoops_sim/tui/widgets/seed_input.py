"""Seed input widget.

Textual widget wrapping Input for seed entry.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Input, Static


class SeedInput(Widget):
    """Seed input with label."""

    def __init__(self, value: int = 42, **kwargs) -> None:
        super().__init__(**kwargs)
        self._value = value

    def compose(self) -> ComposeResult:
        yield Static("Seed:")
        yield Input(value=str(self._value), id="seed-input", type="integer")

    @property
    def value(self) -> int:
        try:
            inp = self.query_one("#seed-input", Input)
            return int(inp.value)
        except (ValueError, Exception):
            return 42
