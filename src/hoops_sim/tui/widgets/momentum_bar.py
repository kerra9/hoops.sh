"""-5 to +5 momentum display."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label


class MomentumBar(Widget):
    """Visual momentum display on a -5 to +5 scale.

    Positive = home team has momentum (green, right).
    Negative = away team has momentum (red, left).
    """

    DEFAULT_CSS = """
    MomentumBar {
        height: 1;
        layout: horizontal;
        width: 100%;
    }
    """

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
        self._value = max(-5.0, min(5.0, value))
        self._home_name = home_name
        self._away_name = away_name

    def compose(self) -> ComposeResult:
        # Build a 20-char bar centered at 10
        bar_len = 20
        center = bar_len // 2
        # Map -5..+5 to 0..20
        pos = int((self._value + 5) / 10 * bar_len)
        pos = max(0, min(bar_len, pos))

        bar_chars = list("\u2591" * bar_len)
        if pos < center:
            for i in range(pos, center):
                bar_chars[i] = "\u2588"
            color = "#e74c3c"  # red for away momentum
        elif pos > center:
            for i in range(center, pos):
                bar_chars[i] = "\u2588"
            color = "#2ecc71"  # green for home momentum
        else:
            color = "#888888"

        bar_str = "".join(bar_chars)
        with Horizontal(classes="momentum-bar"):
            yield Label(f"{self._away_name:<8}")
            yield Label(f"[{color}]{bar_str}[/]")
            yield Label(f"{self._home_name:>8}")

    def update_momentum(self, value: float) -> None:
        """Update the momentum display."""
        self._value = max(-5.0, min(5.0, value))
        self.refresh(recompose=True)
