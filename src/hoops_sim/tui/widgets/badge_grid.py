"""Grid display of player badges with tier-based coloring."""

from __future__ import annotations

from typing import Dict

from textual.app import ComposeResult
from textual.containers import Grid
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.models.badges import BADGE_DEFINITIONS, BadgeTier

# Badge tier colors: bronze -> silver -> gold -> purple (HOF)
TIER_COLORS = {
    BadgeTier.BRONZE: "#cd7f32",
    BadgeTier.SILVER: "#c0c0c0",
    BadgeTier.GOLD: "#ffd700",
    BadgeTier.HALL_OF_FAME: "#9b59b6",
}

TIER_LABELS = {
    BadgeTier.BRONZE: "B",
    BadgeTier.SILVER: "S",
    BadgeTier.GOLD: "G",
    BadgeTier.HALL_OF_FAME: "H",
}


class BadgeGrid(Widget):
    """Grid display of player badges with tier-based coloring.

    Shows each badge the player has with color indicating the tier.
    """

    DEFAULT_CSS = """
    BadgeGrid {
        height: auto;
        width: 100%;
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        padding: 1;
    }
    """

    def __init__(
        self,
        badges: Dict[str, BadgeTier] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._badges = badges or {}

    def compose(self) -> ComposeResult:
        if not self._badges:
            yield Label("[dim]No badges[/]")
            return

        for badge_key, tier in sorted(self._badges.items()):
            defn = BADGE_DEFINITIONS.get(badge_key)
            badge_name = defn.name if defn else badge_key.replace("_", " ").title()
            color = TIER_COLORS.get(tier, "#888888")
            tier_label = TIER_LABELS.get(tier, "?")
            yield Label(f"[{color}][{tier_label}] {badge_name}[/]")

    def update_badges(self, badges: Dict[str, BadgeTier]) -> None:
        """Update displayed badges."""
        self._badges = badges
        self.refresh(recompose=True)
