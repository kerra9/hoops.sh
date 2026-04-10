"""TV-style broadcast scoreboard strip for the live game screen.

Textual widget with reactive properties that auto-update on data change.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget


class BroadcastScoreboard(Widget):
    """TV-style scoreboard: quarter, clock, shot clock, team names, scores.

    Single horizontal strip optimized for the top of the live game screen.
    Uses Textual reactive properties for automatic re-rendering.
    """

    home_score: reactive[int] = reactive(0)
    away_score: reactive[int] = reactive(0)
    quarter: reactive[int] = reactive(1)
    game_clock: reactive[str] = reactive("12:00.0")
    shot_clock: reactive[str] = reactive("24")
    is_overtime: reactive[bool] = reactive(False)
    possession_home: reactive[bool] = reactive(True)

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        home_abbr: str = "HME",
        away_abbr: str = "AWY",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._home_name = home_name
        self._away_name = away_name
        self._home_abbr = home_abbr
        self._away_abbr = away_abbr

    def render(self) -> Text:
        """Build the full scoreboard as a Rich Text object."""
        period = (
            f"OT{self.quarter - 4}" if self.is_overtime else f"Q{self.quarter}"
        )
        poss_arrow = "\u25b6" if self.possession_home else "\u25c0"

        text = Text()
        text.append(f"  {period}", style="bold dim")
        text.append(" | ")
        text.append(self.game_clock, style="bold")
        text.append(" | Shot: ")
        text.append(self.shot_clock, style="bold yellow")
        text.append("   ")
        text.append(f"{self._away_abbr} ", style="bold")
        text.append(f"{self.away_score:>3}", style="bold white")
        text.append(f"  {poss_arrow}  ")
        text.append(f"{self.home_score:<3}", style="bold white")
        text.append(f" {self._home_abbr}", style="bold")
        return text

    def update_state(
        self,
        *,
        home_score: int | None = None,
        away_score: int | None = None,
        quarter: int | None = None,
        game_clock: str | None = None,
        shot_clock: str | None = None,
        is_overtime: bool | None = None,
        possession_home: bool | None = None,
    ) -> None:
        """Bulk update scoreboard state."""
        if is_overtime is not None:
            self.is_overtime = is_overtime
        if quarter is not None:
            self.quarter = quarter
        if game_clock is not None:
            self.game_clock = game_clock
        if shot_clock is not None:
            self.shot_clock = shot_clock
        if home_score is not None:
            self.home_score = home_score
        if away_score is not None:
            self.away_score = away_score
        if possession_home is not None:
            self.possession_home = possession_home
