"""Court shooting chart with zone-colored regions.

Textual widget for displaying player shooting profile by zone.
"""

from __future__ import annotations

from rich.text import Text
from textual.widget import Widget

from hoops_sim.tui.theme import COLD_ZONE, HOT_ZONE, NEUTRAL_ZONE


class CourtShootingChart(Widget):
    """Half-court overlay with zone-colored regions showing FG%."""

    def __init__(self, profile=None, **kwargs) -> None:
        super().__init__(**kwargs)
        self._profile = profile

    def render(self) -> Text:
        text = Text()
        if not self._profile:
            text.append("  No shooting data available", style="dim")
            return text

        zones = [
            ("Paint", "paint"),
            ("Mid-Range", "midrange"),
            ("Three-Point", "three_point"),
            ("Corner 3", "corner_three"),
        ]

        for zone_name, attr in zones:
            pct = getattr(self._profile, attr, None)
            if pct is not None and hasattr(pct, "percentage"):
                val = pct.percentage
            elif isinstance(pct, (int, float)):
                val = pct
            else:
                val = 0.0

            if val >= 0.45:
                color = HOT_ZONE
            elif val >= 0.35:
                color = NEUTRAL_ZONE
            else:
                color = COLD_ZONE

            bar_len = 8
            filled = int(val * bar_len)
            bar = "\u2588" * filled + "\u2591" * (bar_len - filled)
            text.append(f"  {zone_name:<14} ")
            text.append(bar, style=color)
            text.append(f" {val:.0%}\n")
        return text
