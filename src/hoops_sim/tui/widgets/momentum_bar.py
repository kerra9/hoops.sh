"""-5 to +5 momentum display with gradient fill.

Textual widget using reactive properties for smooth updates.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from hoops_sim.tui.theme import MOMENTUM_AWAY, MOMENTUM_HOME, MOMENTUM_NEUTRAL


class MomentumBar(Widget):
    """Visual momentum display on a -5 to +5 scale.

    Positive = home team has momentum (green, right).
    Negative = away team has momentum (red, left).
    Uses Textual reactive properties for automatic re-rendering.
    """

    value: reactive[float] = reactive(0.0)

    def __init__(
        self,
        value: float = 0.0,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._home_name = home_name
        self._away_name = away_name
        self.value = max(-5.0, min(5.0, value))

    def render(self) -> Text:
        """Build the momentum bar as Rich Text."""
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
        text = Text()
        text.append(f"{self._away_name:<8} ")
        text.append(bar_str, style=color)
        text.append(f" {self._home_name:>8}")
        return text

    def update_momentum(self, value: float) -> None:
        """Update the momentum display."""
        self.value = max(-5.0, min(5.0, value))
