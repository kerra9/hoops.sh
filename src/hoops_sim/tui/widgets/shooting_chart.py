"""Zone-based shooting profile display showing hot/cold zones."""

from __future__ import annotations

from hoops_sim.court.zones import Zone, get_zone_info
from hoops_sim.models.shooting_profile import ShootingProfile, ZoneRating
from hoops_sim.tui.base import Widget

ZONE_COLORS = {
    ZoneRating.HOT: "#e74c3c",
    ZoneRating.COLD: "#3498db",
    ZoneRating.NEUTRAL: "#888888",
}


class ShootingChart(Widget):
    """Zone-based shooting profile display."""

    def __init__(
        self,
        profile: ShootingProfile | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._profile = profile or ShootingProfile()

    def render(self) -> str:
        lines = ["Shooting Zones:"]
        for zone in Zone:
            info = get_zone_info(zone)
            rating = self._profile.get_rating(zone)
            modifier = self._profile.get_modifier(zone)
            color = ZONE_COLORS.get(rating, "#888888")
            mod_str = f"+{modifier}" if modifier > 0 else str(modifier)
            icon = (
                "\u2b24"
                if rating == ZoneRating.HOT
                else ("\u25cb" if rating == ZoneRating.COLD else "\u25cf")
            )
            lines.append(f"  [{color}]{icon} {info.short_name:<12} {mod_str:>4}[/]")
        return "\n".join(lines)

    def update_profile(self, profile: ShootingProfile) -> None:
        """Update the shooting chart."""
        self._profile = profile
