"""TV-style broadcast scoreboard strip for the live game screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label


class BroadcastScoreboard(Widget):
    """TV-style scoreboard: quarter, clock, shot clock, team names, scores.

    Single horizontal strip optimized for the top of the live game screen.
    Uses reactive properties for efficient per-tick updates.
    """

    DEFAULT_CSS = """
    BroadcastScoreboard {
        height: 3;
        width: 100%;
        background: $primary-background;
        layout: horizontal;
        align: center middle;
        padding: 0 1;
    }
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

    def compose(self) -> ComposeResult:
        yield Label("", id="bs-display")

    def _render_scoreboard(self) -> str:
        """Build the full scoreboard string."""
        period = (
            f"OT{self.quarter - 4}" if self.is_overtime else f"Q{self.quarter}"
        )
        poss_arrow = "\u25b6" if self.possession_home else "\u25c0"
        away_str = f"{self._away_abbr}"
        home_str = f"{self._home_abbr}"

        return (
            f"  {period} | "
            f"[bold]{self.game_clock}[/] | "
            f"Shot: [yellow]{self.shot_clock}[/]  "
            f"   {away_str} [bold]{self.away_score:>3}[/]"
            f"  {poss_arrow}  "
            f"[bold]{self.home_score:<3}[/] {home_str}"
        )

    def _update_display(self) -> None:
        try:
            self.query_one("#bs-display", Label).update(self._render_scoreboard())
        except Exception:
            pass

    def on_mount(self) -> None:
        self._update_display()

    def watch_home_score(self, _v: int) -> None:
        self._update_display()

    def watch_away_score(self, _v: int) -> None:
        self._update_display()

    def watch_quarter(self, _v: int) -> None:
        self._update_display()

    def watch_game_clock(self, _v: str) -> None:
        self._update_display()

    def watch_shot_clock(self, _v: str) -> None:
        self._update_display()

    def watch_possession_home(self, _v: bool) -> None:
        self._update_display()

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
