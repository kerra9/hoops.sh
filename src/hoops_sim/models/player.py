"""Complete player model combining all sub-models.

A Player brings together body, attributes, tendencies, badges,
shooting profile, personality, and lifestyle into a single entity.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from hoops_sim.models.attributes import PlayerAttributes
from hoops_sim.models.badges import PlayerBadges
from hoops_sim.models.body import PlayerBody
from hoops_sim.models.lifestyle import PlayerLifestyle
from hoops_sim.models.personality import PlayerPersonality
from hoops_sim.models.shooting_profile import ShootingProfile
from hoops_sim.models.tendencies import PlayerTendencies


@dataclass
class PlayerIdentity:
    """Broadcast identity for narration flavor.

    Provides announcer-friendly nicknames, signature moves,
    celebration styles, and play style descriptions used by
    the broadcast layer to add personality to narration.
    """

    announcer_nickname: str = ""       # "The Beard", "Big Fundamental"
    signature_moves: list[str] = field(default_factory=list)  # ["step-back three", "euro step"]
    play_style: str = ""               # "crafty veteran", "explosive athlete"
    celebration_style: str = ""        # "stares down defender", "flexes"
    known_for: list[str] = field(default_factory=list)  # ["deep threes", "lockdown defense"]


class Position(enum.Enum):
    """Player positions."""

    PG = "PG"  # Point Guard
    SG = "SG"  # Shooting Guard
    SF = "SF"  # Small Forward
    PF = "PF"  # Power Forward
    C = "C"  # Center


# Typical height ranges by position (inches)
POSITION_HEIGHT_RANGES = {
    Position.PG: (72, 77),   # 6'0" to 6'5"
    Position.SG: (75, 79),   # 6'3" to 6'7"
    Position.SF: (78, 82),   # 6'6" to 6'10"
    Position.PF: (80, 84),   # 6'8" to 7'0"
    Position.C: (82, 88),    # 6'10" to 7'4"
}


@dataclass
class Player:
    """A complete basketball player.

    Ties together all sub-models: physical body, attributes, tendencies,
    badges, shooting profile, personality, and lifestyle.
    """

    # Identity
    id: int = 0
    first_name: str = ""
    last_name: str = ""
    age: int = 25
    position: Position = Position.SF
    secondary_position: Position | None = None
    jersey_number: int = 0
    years_pro: int = 3

    # Sub-models
    body: PlayerBody = field(default_factory=PlayerBody)
    attributes: PlayerAttributes = field(default_factory=PlayerAttributes)
    tendencies: PlayerTendencies = field(default_factory=PlayerTendencies)
    badges: PlayerBadges = field(default_factory=PlayerBadges)
    shooting_profile: ShootingProfile = field(default_factory=ShootingProfile)
    personality: PlayerPersonality = field(default_factory=PlayerPersonality)
    lifestyle: PlayerLifestyle = field(default_factory=PlayerLifestyle)
    identity: PlayerIdentity = field(default_factory=PlayerIdentity)

    # Runtime state (not part of persistent data)
    current_energy: float = 100.0
    current_morale: float = 0.5  # 0 to 1

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @property
    def overall(self) -> int:
        """Overall rating calculated from attributes."""
        return self.attributes.overall()

    def get_zone_rating(self, zone_key: str) -> int:
        """Get the effective shooting rating for a specific zone.

        Combines base shooting attribute with zone-specific modifier.
        """
        from hoops_sim.court.zones import Zone, get_zone_info

        zone = Zone[zone_key] if isinstance(zone_key, str) else zone_key
        info = get_zone_info(zone)

        # Select base attribute based on zone type
        if info.is_paint:
            base = self.attributes.finishing.layup
        elif info.is_three:
            base = self.attributes.shooting.three_point
        else:
            base = self.attributes.shooting.mid_range

        return self.shooting_profile.get_effective_rating(zone, base)

    def max_energy(self) -> float:
        """Maximum energy based on stamina attribute."""
        from hoops_sim.utils.constants import BASE_ENERGY
        stamina_bonus = self.attributes.athleticism.stamina / 100.0 * 20.0
        return BASE_ENERGY + stamina_bonus

    def energy_pct(self) -> float:
        """Current energy as a percentage of max."""
        max_e = self.max_energy()
        if max_e <= 0:
            return 0.0
        return self.current_energy / max_e

    def is_fatigued(self) -> bool:
        """Check if the player is below 60% energy."""
        return self.energy_pct() < 0.60

    def is_exhausted(self) -> bool:
        """Check if the player is below 20% energy."""
        return self.energy_pct() < 0.20

    def vertical_leap_inches(self) -> float:
        """Vertical leap in inches derived from attribute."""
        # Map 0-99 to ~24-44 inches
        from hoops_sim.utils.math import attribute_to_range
        return attribute_to_range(self.attributes.athleticism.vertical_leap, 24.0, 44.0)

    def can_play_position(self, pos: Position) -> bool:
        """Check if the player can play a given position."""
        return pos == self.position or pos == self.secondary_position

    def is_rookie(self) -> bool:
        return self.years_pro == 0

    def is_veteran(self) -> bool:
        return self.years_pro >= 10

    def __repr__(self) -> str:
        return (
            f"Player('{self.full_name}', {self.position.value}, "
            f"OVR={self.overall}, Age={self.age})"
        )
