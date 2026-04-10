"""Spatial half-court shooting chart with hot/cold zone coloring."""

from __future__ import annotations

from hoops_sim.court.zones import Zone, get_zone_info
from hoops_sim.models.shooting_profile import ShootingProfile, ZoneRating
from hoops_sim.tui.base import Widget
from hoops_sim.tui.theme import COLD_ZONE, HOT_ZONE, NEUTRAL_ZONE

# Zone display characters
_RATING_CHARS = {
    ZoneRating.HOT: "H",
    ZoneRating.COLD: "C",
    ZoneRating.NEUTRAL: "N",
}

_RATING_COLORS = {
    ZoneRating.HOT: HOT_ZONE,
    ZoneRating.COLD: COLD_ZONE,
    ZoneRating.NEUTRAL: NEUTRAL_ZONE,
}

# Spatial layout of zones on a mini half-court grid
_ZONE_LAYOUT = [
    [(0, 0, Zone.THREE_LEFT_CORNER), (0, 4, Zone.THREE_RIGHT_CORNER)],
    [
        (1, 0, Zone.THREE_LEFT_WING),
        (1, 1, Zone.THREE_LEFT_ABOVE_BREAK),
        (1, 2, Zone.THREE_TOP_KEY),
        (1, 3, Zone.THREE_RIGHT_ABOVE_BREAK),
        (1, 4, Zone.THREE_RIGHT_WING),
    ],
    [
        (2, 0, Zone.MID_LEFT_WING),
        (2, 1, Zone.MID_LEFT_ELBOW),
        (2, 2, Zone.MID_FREE_THROW),
        (2, 3, Zone.MID_RIGHT_ELBOW),
        (2, 4, Zone.MID_RIGHT_WING),
    ],
    [
        (3, 0, Zone.CLOSE_LEFT),
        (3, 1, Zone.CLOSE_BASELINE),
        (3, 2, Zone.CLOSE_MIDDLE),
        (3, 3, Zone.CLOSE_BASELINE),
        (3, 4, Zone.CLOSE_RIGHT),
    ],
    [(4, 2, Zone.RESTRICTED)],
]


class CourtShootingChart(Widget):
    """Spatial half-court with hot/cold zone coloring."""

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
        """Render the spatial shooting chart."""
        lines = []
        lines.append("     Shooting Chart")
        lines.append("  +----- 3PT ARC -----+")

        grid = [["     "] * 5 for _ in range(5)]

        for row_zones in _ZONE_LAYOUT:
            for row, col, zone in row_zones:
                rating = self._profile.get_rating(zone)
                char = _RATING_CHARS.get(rating, "?")
                color = _RATING_COLORS.get(rating, NEUTRAL_ZONE)
                info = get_zone_info(zone)
                short = info.short_name[:5]
                grid[row][col] = f"[{color}]{char}:{short:<3}[/]"

        for row in grid:
            lines.append("  " + " ".join(cell for cell in row))

        lines.append("  +------- RIM -------+")
        return "\n".join(lines)

    def update_profile(self, profile: ShootingProfile) -> None:
        """Update the chart data."""
        self._profile = profile
