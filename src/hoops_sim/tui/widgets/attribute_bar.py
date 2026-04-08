"""Horizontal attribute bar 0-99 with color gradient."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label


def _rating_color(value: int) -> str:
    """Return a color string based on rating value (0-99)."""
    if value >= 90:
        return "#2ecc71"  # green
    if value >= 80:
        return "#27ae60"  # dark green
    if value >= 70:
        return "#f1c40f"  # yellow
    if value >= 60:
        return "#e67e22"  # orange
    if value >= 50:
        return "#e74c3c"  # red
    return "#c0392b"  # dark red


class AttributeBar(Widget):
    """Horizontal bar displaying a 0-99 attribute rating with color gradient.

    Args:
        label: The attribute name to display.
        value: The rating value (0-99).
    """

    DEFAULT_CSS = """
    AttributeBar {
        height: 1;
        layout: horizontal;
    }
    """

    def __init__(
        self,
        label: str,
        value: int = 50,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._label = label
        self._value = max(0, min(99, value))

    def compose(self) -> ComposeResult:
        bar_width = self._value // 5  # Scale to ~20 chars
        color = _rating_color(self._value)
        filled = "\u2588" * bar_width
        empty = "\u2591" * (20 - bar_width)
        with Horizontal(classes="attribute-bar"):
            yield Label(f"{self._label:<16}", classes="attribute-bar-label")
            yield Label(f"[{color}]{filled}[/]{empty}", classes="attribute-bar-fill")
            yield Label(f"{self._value:>3}", classes="attribute-bar-value")

    def update_value(self, value: int) -> None:
        """Update the displayed value and re-render."""
        self._value = max(0, min(99, value))
        self.refresh(recompose=True)
