"""Spatial half-court shooting chart with hot/cold zone coloring."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Static

from hoops_sim.court.zones import Zone, get_zone_info
from hoops_sim.models.shooting_profile import ShootingProfile, ZoneRating
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
# Each cell is (row, col) -> Zone
# The grid is roughly 5 rows x 5 cols representing court areas
_ZONE_LAYOUT = [
    # Row 0: Corner 3s and deep
    [(0, 0, Zone.THREE_LEFT_CORNER), (0, 4, Zone.THREE_RIGHT_CORNER)],
    # Row 1: Wings and above-break 3s
    [
        (1, 0, Zone.THREE_LEFT_WING),
        (1, 1, Zone.THREE_LEFT_ABOVE_BREAK),
        (1, 2, Zone.THREE_TOP_KEY),
        (1, 3, Zone.THREE_RIGHT_ABOVE_BREAK),
        (1, 4, Zone.THREE_RIGHT_WING),
    ],
    # Row 2: Mid-range
    [
        (2, 0, Zone.MID_LEFT_WING),
        (2, 1, Zone.MID_LEFT_ELBOW),
        (2, 2, Zone.MID_FREE_THROW),
        (2, 3, Zone.MID_RIGHT_ELBOW),
        (2, 4, Zone.MID_RIGHT_WING),
    ],
    # Row 3: Close range
    [
        (3, 0, Zone.CLOSE_LEFT),
        (3, 1, Zone.CLOSE_BASELINE),
        (3, 2, Zone.CLOSE_MIDDLE),
        (3, 3, Zone.CLOSE_BASELINE),
        (3, 4, Zone.CLOSE_RIGHT),
    ],
    # Row 4: Restricted area
    [(4, 2, Zone.RESTRICTED)],
]


class CourtShootingChart(Widget):
    """Spatial half-court with hot/cold zone coloring.

    Shows each zone as a colored cell in a spatial layout.
    """

    DEFAULT_CSS = """
    CourtShootingChart {
        height: 10;
        width: 30;
        padding: 0;
    }
    """

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

    def compose(self) -> ComposeResult:
        yield Static(self._render_chart(), id="shooting-chart-canvas")

    def _render_chart(self) -> str:
        """Render the spatial shooting chart."""
        lines = []
        lines.append("     Shooting Chart")
        lines.append("  +----- 3PT ARC -----+")

        # Build a 5x5 grid
        grid = [["     "] * 5 for _ in range(5)]

        for row_zones in _ZONE_LAYOUT:
            for row, col, zone in row_zones:
                rating = self._profile.get_rating(zone)
                char = _RATING_CHARS.get(rating, "?")
                color = _RATING_COLORS.get(rating, NEUTRAL_ZONE)
                grid[row][col] = f"[{color}][{char}][/]"

        for row in grid:
            line = "  " + "  ".join(cell for cell in row)
            lines.append(line)

        lines.append("  +-------------------+")
        lines.append("  H=Hot  C=Cold  N=Neutral")
        return "\n".join(lines)

    def update_profile(self, profile: ShootingProfile) -> None:
        """Update the shooting chart."""
        self._profile = profile
        try:
            self.query_one("#shooting-chart-canvas", Static).update(
                self._render_chart()
            )
        except Exception:
            pass
