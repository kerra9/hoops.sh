"""Horizontal attribute bar 0-99 with color gradient."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import rating_color


class AttributeBar(Widget):
    """Horizontal bar displaying a 0-99 attribute rating with color gradient.

    Uses reactive properties for efficient updates.
    """

    DEFAULT_CSS = """
    AttributeBar {
        height: 1;
        layout: horizontal;
    }
    """

    value: reactive[int] = reactive(50)

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
        self.value = max(0, min(99, value))

    def compose(self) -> ComposeResult:
        yield Label("", id="attr-display")

    def _render_bar(self) -> str:
        bar_width = self.value // 5
        color = rating_color(self.value)
        filled = "\u2588" * bar_width
        empty = "\u2591" * (20 - bar_width)
        return f"{self._label:<14} [{color}]{filled}[/]{empty} {self.value:>3}"

    def watch_value(self, _val: int) -> None:
        try:
            self.query_one("#attr-display", Label).update(self._render_bar())
        except Exception:
            pass

    def on_mount(self) -> None:
        try:
            self.query_one("#attr-display", Label).update(self._render_bar())
        except Exception:
            pass

    def update_value(self, value: int) -> None:
        """Update the displayed value."""
        self.value = max(0, min(99, value))
