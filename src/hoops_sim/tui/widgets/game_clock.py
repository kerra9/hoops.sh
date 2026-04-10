"""Large-format game clock and shot clock with quarter indicator."""

from __future__ import annotations

from hoops_sim.tui.base import Widget


class GameClockDisplay(Widget):
    """Large-format game clock and shot clock with quarter indicator."""

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

    def render(self) -> str:
        period = f"OT{self.quarter - 4}" if self.is_overtime else f"Q{self.quarter}"
        return (
            f"  {period}\n"
            f"  [green]{self.game_clock}[/]\n"
            f"  Shot: [yellow]{self.shot_clock}[/]"
        )

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
