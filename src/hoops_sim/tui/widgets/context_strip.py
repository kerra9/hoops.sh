"""Context strip showing current play, possession, fouls, energy.

Textual widget using reactive properties and Rich Text rendering.
"""

from __future__ import annotations

from rich.text import Text
from textual.reactive import reactive
from textual.widget import Widget

from hoops_sim.tui.theme import MOMENTUM_AWAY, MOMENTUM_HOME, MOMENTUM_NEUTRAL


class ContextStrip(Widget):
    """Bottom strip showing game context: momentum, play, possession, fouls, energy."""

    momentum: reactive[float] = reactive(0.0)

    def __init__(
        self,
        home_name: str = "HOME",
        away_name: str = "AWAY",
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._home_name = home_name
        self._away_name = away_name
        self.current_play = "Half-Court Set"
        self.possession_team = ""
        self.home_fouls = 0
        self.away_fouls = 0
        self.lowest_energy = ""

    def render(self) -> Text:
        """Build the context strip as Rich Text."""
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

        text = Text()
        text.append(f"MOMENTUM  {self._away_name[:3]} ")
        text.append(bar_str, style=color)
        text.append(f" {self._home_name[:3]}")
        if self.lowest_energy:
            text.append(f"  | EN: {self.lowest_energy}")
        text.append("\n")
        text.append(
            f"PLAY: {self.current_play:<20} | "
            f"POSS: {self.possession_team:<6} | "
            f"FOULS: {self.away_fouls}-{self.home_fouls}"
        )
        return text

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
