"""Visual fatigue meter mapping to the 5 fatigue tiers."""

from __future__ import annotations

from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import energy_color

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

    def __init__(
        self,
        label: str = "Energy",
        energy_pct: float = 1.0,
        fatigue_tier: int = 0,
        *,
        compact: bool = False,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._label = label
        self._compact = compact
        self.energy_pct = max(0.0, min(1.0, energy_pct))
        self.fatigue_tier = max(0, min(5, fatigue_tier))

    def render(self) -> str:
        """Build the energy gauge string."""
        tier_name, color = FATIGUE_TIERS.get(self.fatigue_tier, ("?", "#888888"))
        if self._compact:
            bar_width = int(self.energy_pct * 5)
            filled = "\u2588" * bar_width
            empty = "\u2591" * (5 - bar_width)
            return f"[{color}]{filled}{empty}[/]"
        bar_width = int(self.energy_pct * 20)
        filled = "\u2588" * bar_width
        empty = "\u2591" * (20 - bar_width)
        pct_text = f"{self.energy_pct * 100:.0f}%"
        return (
            f"{self._label:<10} [{color}]{filled}[/]{empty}"
            f" [{color}]{pct_text:>4} {tier_name}[/]"
        )

    def update_energy(self, energy_pct: float, fatigue_tier: int) -> None:
        """Update the energy display."""
        self.energy_pct = max(0.0, min(1.0, energy_pct))
        self.fatigue_tier = max(0, min(5, fatigue_tier))
