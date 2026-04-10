"""Context strip showing current play, possession, fouls, energy."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import MOMENTUM_AWAY, MOMENTUM_HOME, MOMENTUM_NEUTRAL


class ContextStrip(Widget):
    """Bottom strip showing game context: momentum, play, possession, fouls, energy.

    Uses reactive properties for efficient updates on possession/play changes.
    """

    DEFAULT_CSS = """
    ContextStrip {
        height: 2;
        width: 100%;
        background: $primary-background;
        padding: 0 1;
    }
    """

    momentum: reactive[float] = reactive(0.0)
    current_play: reactive[str] = reactive("Half-Court Set")
    possession_team: reactive[str] = reactive("")
    home_fouls: reactive[int] = reactive(0)
    away_fouls: reactive[int] = reactive(0)
    lowest_energy: reactive[str] = reactive("")

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._home_name = home_name
        self._away_name = away_name

    def compose(self) -> ComposeResult:
        yield Label("", id="ctx-line1")
        yield Label("", id="ctx-line2")

    def _render(self) -> tuple[str, str]:
        """Build both context lines."""
        # Line 1: Momentum bar
        bar_len = 20
        center = bar_len // 2
        clamped = max(-5.0, min(5.0, self.momentum))
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
        line1 = (
            f"MOMENTUM  {self._away_name[:3]} "
            f"[{color}]{bar_str}[/] "
            f"{self._home_name[:3]}"
        )
        if self.lowest_energy:
            line1 += f"  | EN: {self.lowest_energy}"

        # Line 2: Play, possession, fouls
        line2 = (
            f"PLAY: {self.current_play:<20} | "
            f"POSS: {self.possession_team:<6} | "
            f"FOULS: {self.away_fouls}-{self.home_fouls}"
        )
        return line1, line2

    def _update_display(self) -> None:
        try:
            line1, line2 = self._render()
            self.query_one("#ctx-line1", Label).update(line1)
            self.query_one("#ctx-line2", Label).update(line2)
        except Exception:
            pass

    def on_mount(self) -> None:
        self._update_display()

    def watch_momentum(self, _v: float) -> None:
        self._update_display()

    def watch_current_play(self, _v: str) -> None:
        self._update_display()

    def watch_possession_team(self, _v: str) -> None:
        self._update_display()

    def watch_home_fouls(self, _v: int) -> None:
        self._update_display()

    def watch_away_fouls(self, _v: int) -> None:
        self._update_display()

    def update_context(
        self,
        *,
        momentum: float | None = None,
        current_play: str | None = None,
        possession_team: str | None = None,
        home_fouls: int | None = None,
        away_fouls: int | None = None,
        lowest_energy: str | None = None,
    ) -> None:
        """Bulk update context strip."""
        if momentum is not None:
            self.momentum = momentum
        if current_play is not None:
            self.current_play = current_play
        if possession_team is not None:
            self.possession_team = possession_team
        if home_fouls is not None:
            self.home_fouls = home_fouls
        if away_fouls is not None:
            self.away_fouls = away_fouls
        if lowest_energy is not None:
            self.lowest_energy = lowest_energy
