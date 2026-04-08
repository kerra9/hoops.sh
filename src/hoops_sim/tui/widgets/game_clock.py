"""Large-format game clock and shot clock with quarter indicator."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label


class GameClockDisplay(Widget):
    """Large-format game clock and shot clock with quarter indicator.

    Reads from GameClock data to display the current game time.
    """

    DEFAULT_CSS = """
    GameClockDisplay {
        height: 3;
        width: 22;
        border: tall $primary;
        text-align: center;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        quarter: int = 1,
        game_clock: str = "12:00.0",
        shot_clock: str = "24",
        is_overtime: bool = False,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._quarter = quarter
        self._game_clock = game_clock
        self._shot_clock = shot_clock
        self._is_overtime = is_overtime

    def compose(self) -> ComposeResult:
        period = f"OT{self._quarter - 4}" if self._is_overtime else f"Q{self._quarter}"
        with Vertical():
            yield Label(f"  {period}", id="clock-quarter")
            yield Label(f"  [$success]{self._game_clock}[/]", id="clock-game")
            yield Label(f"  Shot: [$warning]{self._shot_clock}[/]", id="clock-shot")

    def update_clock(
        self,
        quarter: int,
        game_clock: str,
        shot_clock: str,
        is_overtime: bool = False,
    ) -> None:
        """Update the clock display."""
        self._quarter = quarter
        self._game_clock = game_clock
        self._shot_clock = shot_clock
        self._is_overtime = is_overtime
        self.refresh(recompose=True)
