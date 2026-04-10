"""Large-format game clock and shot clock with quarter indicator."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class GameClockDisplay(Widget):
    """Large-format game clock and shot clock with quarter indicator.

    Uses reactive properties for efficient per-tick updates.
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

    quarter: reactive[int] = reactive(1)
    game_clock: reactive[str] = reactive("12:00.0")
    shot_clock: reactive[str] = reactive("24")
    is_overtime: reactive[bool] = reactive(False)

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
        self.quarter = quarter
        self.game_clock = game_clock
        self.shot_clock = shot_clock
        self.is_overtime = is_overtime

    def compose(self) -> ComposeResult:
        period = f"OT{self.quarter - 4}" if self.is_overtime else f"Q{self.quarter}"
        with Vertical():
            yield Label(f"  {period}", id="clock-quarter")
            yield Label(f"  [green]{self.game_clock}[/]", id="clock-game")
            yield Label(f"  Shot: [yellow]{self.shot_clock}[/]", id="clock-shot")

    def _update_labels(self) -> None:
        """Surgically update clock labels."""
        try:
            period = (
                f"OT{self.quarter - 4}" if self.is_overtime else f"Q{self.quarter}"
            )
            self.query_one("#clock-quarter", Label).update(f"  {period}")
            self.query_one("#clock-game", Label).update(
                f"  [green]{self.game_clock}[/]"
            )
            self.query_one("#clock-shot", Label).update(
                f"  Shot: [yellow]{self.shot_clock}[/]"
            )
        except Exception:
            pass

    def watch_quarter(self, _value: int) -> None:
        self._update_labels()

    def watch_game_clock(self, _value: str) -> None:
        self._update_labels()

    def watch_shot_clock(self, _value: str) -> None:
        self._update_labels()

    def update_clock(
        self,
        quarter: int,
        game_clock: str,
        shot_clock: str,
        is_overtime: bool = False,
    ) -> None:
        """Update the clock display."""
        self.is_overtime = is_overtime
        self.quarter = quarter
        self.game_clock = game_clock
        self.shot_clock = shot_clock
