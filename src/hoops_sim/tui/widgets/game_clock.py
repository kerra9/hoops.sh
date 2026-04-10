"""Game clock widget.

Textual widget for displaying the game clock.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class GameClock(Widget):
    """Game clock display."""

    display: reactive[str] = reactive("12:00.0")
    quarter: reactive[int] = reactive(1)

    def render(self) -> Text:
        period = f"Q{self.quarter}" if self.quarter <= 4 else f"OT{self.quarter - 4}"
        text = Text()
        text.append(f"{period} ", style="bold dim")
        text.append(self.display, style="bold")
        return text
