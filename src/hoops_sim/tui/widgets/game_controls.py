"""Speed control bar widget for live game screen.

Textual widget providing simulation speed controls.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget


SPEED_LEVELS = [
    ("0.5x", 2.0),
    ("1x", 1.0),
    ("2x", 0.5),
    ("4x", 0.25),
    ("Instant", 0.0),
]


class GameControls(Widget):
    """Speed control bar showing current simulation speed."""

    def __init__(self, current_index: int = 1, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_index = current_index

    def render(self) -> Text:
        text = Text()
        text.append("Speed: ")
        for i, (label, _) in enumerate(SPEED_LEVELS):
            if i == self._current_index:
                text.append(f"[{label}]", style="bold reverse")
            else:
                text.append(f" {label} ", style="dim")
        return text

    def speed_up(self) -> tuple[str, float]:
        """Increase speed, return (label, delay)."""
        self._current_index = min(len(SPEED_LEVELS) - 1, self._current_index + 1)
        self.refresh()
        return SPEED_LEVELS[self._current_index]

    def slow_down(self) -> tuple[str, float]:
        """Decrease speed, return (label, delay)."""
        self._current_index = max(0, self._current_index - 1)
        self.refresh()
        return SPEED_LEVELS[self._current_index]

    @property
    def current_delay(self) -> float:
        return SPEED_LEVELS[self._current_index][1]

    @property
    def current_label(self) -> str:
        return SPEED_LEVELS[self._current_index][0]
