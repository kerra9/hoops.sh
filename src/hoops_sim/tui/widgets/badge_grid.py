"""Badge grid showing earned badges with tier colors.

Textual widget for displaying player badges.
"""

from __future__ import annotations

from typing import Dict

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import BADGE_BRONZE, BADGE_GOLD, BADGE_HOF, BADGE_SILVER

_TIER_COLORS = {
    "bronze": BADGE_BRONZE,
    "silver": BADGE_SILVER,
    "gold": BADGE_GOLD,
    "hof": BADGE_HOF,
    "hall_of_fame": BADGE_HOF,
}

_TIER_ICONS = {
    "bronze": "\u25cb",
    "silver": "\u25d0",
    "gold": "\u25cf",
    "hof": "\u2605",
    "hall_of_fame": "\u2605",
}


class BadgeGrid(Widget):
    """Grid of badge icons with tier-colored display."""

    def __init__(
        self,
        badges: Dict | None = None,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._badges = badges or {}

    def render(self) -> Text:
        text = Text()
        items = []
        for badge_name, tier in self._badges.items():
            tier_str = str(tier).lower() if not isinstance(tier, str) else tier.lower()
            # Handle enum values
            if hasattr(tier, "value"):
                tier_str = str(tier.value).lower()
            color = _TIER_COLORS.get(tier_str, BADGE_BRONZE)
            icon = _TIER_ICONS.get(tier_str, "\u25cb")
            items.append((icon, badge_name, color))

        if not items:
            text.append("  No badges earned", style="dim")
            return text

        for i, (icon, name, color) in enumerate(items):
            if i > 0 and i % 3 == 0:
                text.append("\n")
            text.append(f"  {icon} ", style=color)
            text.append(f"{name:<18}")
        return text
