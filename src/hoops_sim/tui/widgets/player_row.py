"""Single-player stat line used in tables."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.widgets.energy_gauge import FATIGUE_TIERS


class PlayerRow(Widget):
    """A single player row showing name, position, key stats, and energy.

    Designed for use in roster tables and mini box scores.
    """

    DEFAULT_CSS = """
    PlayerRow {
        height: 1;
        layout: horizontal;
    }
    """

    def __init__(
        self,
        player_name: str,
        position: str = "",
        overall: int = 0,
        stats_text: str = "",
        energy_pct: float = 1.0,
        fatigue_tier: int = 0,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._player_name = player_name
        self._position = position
        self._overall = overall
        self._stats_text = stats_text
        self._energy_pct = energy_pct
        self._fatigue_tier = fatigue_tier

    def compose(self) -> ComposeResult:
        _, color = FATIGUE_TIERS.get(self._fatigue_tier, ("?", "#888888"))
        energy_bar_w = int(self._energy_pct * 8)
        filled = "\u2588" * energy_bar_w
        empty = "\u2591" * (8 - energy_bar_w)
        energy_bar = f"[{color}]{filled}{empty}[/]"
        with Horizontal(classes="player-row"):
            yield Label(f"{self._player_name:<20}", classes="player-row-name")
            yield Label(f"{self._position:<4}", classes="player-row-pos")
            yield Label(f"{self._overall:>3} ", classes="player-row-ovr")
            yield Label(f"{self._stats_text:<30}", classes="player-row-stats")
            yield Label(energy_bar, classes="player-row-energy")
