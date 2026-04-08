"""Hot zone system: 17-zone personal shot chart.

Each player has a shooting profile that tracks their effectiveness in each
of the 17 court zones. This is separate from raw shooting attributes --
it represents the player's comfort and history in each zone.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict

from hoops_sim.court.zones import Zone


class ZoneRating(enum.Enum):
    """Hot/cold zone classification for a zone."""

    COLD = "cold"  # Below average
    NEUTRAL = "neutral"  # Average
    HOT = "hot"  # Above average


@dataclass
class ShootingProfile:
    """A player's personal shooting effectiveness by zone.

    Each zone has a modifier that adjusts the player's base shooting
    percentage. A modifier of 0 means the player shoots at their base
    rate in that zone; positive means better, negative means worse.

    Attributes:
        zone_modifiers: Per-zone modifier (-15 to +15).
        preferred_zones: Zones where the player is most comfortable.
    """

    zone_modifiers: Dict[Zone, int] = field(default_factory=dict)

    def __post_init__(self) -> None:
        # Initialize all zones to neutral if not provided
        for zone in Zone:
            if zone not in self.zone_modifiers:
                self.zone_modifiers[zone] = 0

    def get_modifier(self, zone: Zone) -> int:
        """Get the shooting modifier for a zone."""
        return self.zone_modifiers.get(zone, 0)

    def get_rating(self, zone: Zone) -> ZoneRating:
        """Get the hot/cold classification for a zone."""
        mod = self.get_modifier(zone)
        if mod >= 5:
            return ZoneRating.HOT
        if mod <= -5:
            return ZoneRating.COLD
        return ZoneRating.NEUTRAL

    def set_modifier(self, zone: Zone, value: int) -> None:
        """Set the shooting modifier for a zone (clamped to -15..+15)."""
        self.zone_modifiers[zone] = max(-15, min(15, value))

    def get_effective_rating(self, zone: Zone, base_rating: int) -> int:
        """Calculate effective shooting rating in a zone.

        Combines the player's base shooting rating with their zone modifier.

        Args:
            zone: The court zone.
            base_rating: Base shooting attribute (0-99).

        Returns:
            Adjusted rating clamped to 0-99.
        """
        modifier = self.get_modifier(zone)
        return max(0, min(99, base_rating + modifier))

    def hot_zones(self) -> list:
        """Get all zones where the player is 'hot'."""
        return [z for z in Zone if self.get_rating(z) == ZoneRating.HOT]

    def cold_zones(self) -> list:
        """Get all zones where the player is 'cold'."""
        return [z for z in Zone if self.get_rating(z) == ZoneRating.COLD]

    def zone_count_by_rating(self) -> Dict[ZoneRating, int]:
        """Count zones by rating category."""
        counts: Dict[ZoneRating, int] = {r: 0 for r in ZoneRating}
        for zone in Zone:
            counts[self.get_rating(zone)] += 1
        return counts
