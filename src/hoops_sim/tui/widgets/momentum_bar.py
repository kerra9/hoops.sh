"""-5 to +5 momentum display with gradient fill."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import MOMENTUM_AWAY, MOMENTUM_HOME, MOMENTUM_NEUTRAL


class MomentumBar(Widget):
    """Visual momentum display on a -5 to +5 scale.

    Positive = home team has momentum (green, right).
    Negative = away team has momentum (red, left).
    Uses reactive properties for efficient updates.
    """

    DEFAULT_CSS = """
    MomentumBar {
        height: 1;
        layout: horizontal;
        width: 100%;
    }
    """

    value: reactive[float] = reactive(0.0)

    def __init__(
        self,
        value: float = 0.0,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._home_name = home_name
        self._away_name = away_name
        self.value = max(-5.0, min(5.0, value))

    def compose(self) -> ComposeResult:
        yield Label("", id="momentum-display")

    def _render_bar(self) -> str:
        """Build the momentum bar string."""
        bar_len = 20
        center = bar_len // 2
        clamped = max(-5.0, min(5.0, self.value))
        pos = int((clamped + 5) / 10 * bar_len)
        pos = max(0, min(bar_len, pos))

        bar_chars = list("\u2591" * bar_len)
        if pos < center:
            for i in range(pos, center):
                bar_chars[i] = "\u2588"
            color = MOMENTUM_AWAY
        elif pos > center:
            for i in range(center, pos):
                bar_chars[i] = "\u2588"
            color = MOMENTUM_HOME
        else:
            color = MOMENTUM_NEUTRAL

        bar_str = "".join(bar_chars)
        return f"{self._away_name:<8} [{color}]{bar_str}[/] {self._home_name:>8}"

    def watch_value(self, _val: float) -> None:
        """React to momentum changes."""
        try:
            self.query_one("#momentum-display", Label).update(self._render_bar())
        except Exception:
            pass

    def on_mount(self) -> None:
        try:
            self.query_one("#momentum-display", Label).update(self._render_bar())
        except Exception:
            pass

    def update_momentum(self, value: float) -> None:
        """Update the momentum display."""
        self.value = max(-5.0, min(5.0, value))
