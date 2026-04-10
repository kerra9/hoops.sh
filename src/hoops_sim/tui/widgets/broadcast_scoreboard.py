"""TV-style broadcast scoreboard strip for the live game screen."""

from __future__ import annotations

from hoops_sim.tui.base import Widget


class BroadcastScoreboard(Widget):
    """TV-style scoreboard: quarter, clock, shot clock, team names, scores.

    Single horizontal strip optimized for the top of the live game screen.
    """

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        home_abbr: str = "HME",
        away_abbr: str = "AWY",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._home_name = home_name
        self._away_name = away_name
        self._home_abbr = home_abbr
        self._away_abbr = away_abbr
        self.home_score = 0
        self.away_score = 0
        self.quarter = 1
        self.game_clock = "12:00.0"
        self.shot_clock = "24"
        self.is_overtime = False
        self.possession_home = True

    def render(self) -> str:
        """Build the full scoreboard string."""
        period = (
            f"OT{self.quarter - 4}" if self.is_overtime else f"Q{self.quarter}"
        )
        poss_arrow = "\u25b6" if self.possession_home else "\u25c0"
        return (
            f"  {period} | "
            f"[bold]{self.game_clock}[/] | "
            f"Shot: [yellow]{self.shot_clock}[/]  "
            f"   {self._away_abbr} [bold]{self.away_score:>3}[/]"
            f"  {poss_arrow}  "
            f"[bold]{self.home_score:<3}[/] {self._home_abbr}"
        )

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
