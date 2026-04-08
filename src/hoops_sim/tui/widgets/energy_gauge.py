"""Visual fatigue meter mapping to the 5 fatigue tiers."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widget import Widget
from textual.widgets import Label

# Tier labels and colors matching physical/energy.py fatigue tiers
FATIGUE_TIERS = {
    0: ("Fresh", "#2ecc71"),
    1: ("Light", "#f1c40f"),
    2: ("Moderate", "#e67e22"),
    3: ("Heavy", "#e74c3c"),
    4: ("Exhausted", "#c0392b"),
    5: ("Gassed", "#8b0000"),
}


class EnergyGauge(Widget):
    """Visual fatigue meter for a player's energy level.

    Displays a bar colored by fatigue tier with the current energy percentage.
    """

    DEFAULT_CSS = """
    EnergyGauge {
        height: 1;
        layout: horizontal;
    }
    """

    def __init__(
        self,
        label: str = "Energy",
        energy_pct: float = 1.0,
        fatigue_tier: int = 0,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._label = label
        self._energy_pct = max(0.0, min(1.0, energy_pct))
        self._fatigue_tier = max(0, min(5, fatigue_tier))

    def compose(self) -> ComposeResult:
        tier_name, color = FATIGUE_TIERS.get(self._fatigue_tier, ("?", "#888888"))
        bar_width = int(self._energy_pct * 20)
        filled = "\u2588" * bar_width
        empty = "\u2591" * (20 - bar_width)
        pct_text = f"{self._energy_pct * 100:.0f}%"
        with Horizontal(classes="energy-gauge"):
            yield Label(f"{self._label:<10}", classes="energy-label")
            yield Label(f"[{color}]{filled}[/]{empty}", classes="energy-fill")
            yield Label(f" [{color}]{pct_text:>4} {tier_name}[/]", classes="energy-value")

    def update_energy(self, energy_pct: float, fatigue_tier: int) -> None:
        """Update the energy display."""
        self._energy_pct = max(0.0, min(1.0, energy_pct))
        self._fatigue_tier = max(0, min(5, fatigue_tier))
        self.refresh(recompose=True)
