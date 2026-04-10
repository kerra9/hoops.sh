"""Grid display of player badges with tier-based coloring."""

from __future__ import annotations

from typing import Dict

from hoops_sim.models.badges import BADGE_DEFINITIONS, BadgeTier
from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import BADGE_BRONZE, BADGE_GOLD, BADGE_HOF, BADGE_SILVER

# Badge tier colors
TIER_COLORS = {
    BadgeTier.BRONZE: BADGE_BRONZE,
    BadgeTier.SILVER: BADGE_SILVER,
    BadgeTier.GOLD: BADGE_GOLD,
    BadgeTier.HALL_OF_FAME: BADGE_HOF,
}

TIER_LABELS = {
    BadgeTier.BRONZE: "B",
    BadgeTier.SILVER: "S",
    BadgeTier.GOLD: "G",
    BadgeTier.HALL_OF_FAME: "H",
}


class BadgeGrid(Widget):
    """Compact grid display of player badges with tier-based coloring."""

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

    def render(self) -> str:
        if not self._badges:
            return "[dim]No badges[/]"
        parts = []
        for badge_key, tier in sorted(self._badges.items()):
            defn = BADGE_DEFINITIONS.get(badge_key)
            badge_name = defn.name if defn else badge_key.replace("_", " ").title()
            color = TIER_COLORS.get(tier, "#888888")
            tier_label = TIER_LABELS.get(tier, "?")
            parts.append(f"[{color}][{tier_label}] {badge_name}[/]")
        return "  ".join(parts)

    def update_badges(self, badges: Dict[str, BadgeTier]) -> None:
        """Update displayed badges."""
        self._badges = badges
