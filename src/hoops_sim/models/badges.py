"""Badge system with 30+ badges across 4 tiers.

Badges represent special abilities that go beyond raw attribute ratings.
A player can have multiple badges, each at one of four tiers.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class BadgeTier(enum.IntEnum):
    """Badge tier levels. Higher tier = stronger effect."""

    BRONZE = 1
    SILVER = 2
    GOLD = 3
    HALL_OF_FAME = 4


class BadgeCategory(enum.Enum):
    """Badge categories."""

    SHOOTING = "shooting"
    FINISHING = "finishing"
    PLAYMAKING = "playmaking"
    DEFENSE = "defense"
    REBOUNDING = "rebounding"
    MENTAL = "mental"


@dataclass(frozen=True)
class BadgeDefinition:
    """Definition of a badge type."""

    name: str
    category: BadgeCategory
    description: str


# All available badges
BADGE_DEFINITIONS: Dict[str, BadgeDefinition] = {
    # Shooting badges
    "catch_and_shoot": BadgeDefinition(
        "Catch and Shoot", BadgeCategory.SHOOTING,
        "Boost to shots taken immediately after catching a pass.",
    ),
    "corner_specialist": BadgeDefinition(
        "Corner Specialist", BadgeCategory.SHOOTING,
        "Boost to three-point shots from the corners.",
    ),
    "deadeye": BadgeDefinition(
        "Deadeye", BadgeCategory.SHOOTING,
        "Reduces penalty from contested shots.",
    ),
    "deep_threes": BadgeDefinition(
        "Deep Threes", BadgeCategory.SHOOTING,
        "Extended range on three-point shots.",
    ),
    "green_machine": BadgeDefinition(
        "Green Machine", BadgeCategory.SHOOTING,
        "Increased bonus on consecutive excellent releases.",
    ),
    "hot_zone_hunter": BadgeDefinition(
        "Hot Zone Hunter", BadgeCategory.SHOOTING,
        "Extra boost when shooting from personal hot zones.",
    ),
    "ice_in_veins": BadgeDefinition(
        "Ice in Veins", BadgeCategory.SHOOTING,
        "Improved free throw and clutch shooting.",
    ),
    "volume_shooter": BadgeDefinition(
        "Volume Shooter", BadgeCategory.SHOOTING,
        "Gets better as shot attempts increase.",
    ),

    # Finishing badges
    "acrobat": BadgeDefinition(
        "Acrobat", BadgeCategory.FINISHING,
        "Boost to layups with difficult body positions (reverse, euro-step).",
    ),
    "contact_finisher": BadgeDefinition(
        "Contact Finisher", BadgeCategory.FINISHING,
        "Boost to layups and dunks through contact.",
    ),
    "giant_slayer": BadgeDefinition(
        "Giant Slayer", BadgeCategory.FINISHING,
        "Boost to finishing against taller defenders.",
    ),
    "posterizer": BadgeDefinition(
        "Posterizer", BadgeCategory.FINISHING,
        "Increased dunk frequency and poster dunk chance.",
    ),
    "slithery_finisher": BadgeDefinition(
        "Slithery Finisher", BadgeCategory.FINISHING,
        "Ability to avoid contact and finish with finesse.",
    ),
    "putback_boss": BadgeDefinition(
        "Putback Boss", BadgeCategory.FINISHING,
        "Boost to putback layups and dunks after offensive rebounds.",
    ),
    "dream_shake": BadgeDefinition(
        "Dream Shake", BadgeCategory.FINISHING,
        "Improved post moves and fakes effectiveness.",
    ),

    # Playmaking badges
    "dimer": BadgeDefinition(
        "Dimer", BadgeCategory.PLAYMAKING,
        "Boost to teammate's shot when this player is the passer.",
    ),
    "needle_threader": BadgeDefinition(
        "Needle Threader", BadgeCategory.PLAYMAKING,
        "Improved passing through tight passing lanes.",
    ),
    "floor_general": BadgeDefinition(
        "Floor General", BadgeCategory.PLAYMAKING,
        "Boosts teammates' offensive attributes when on the court.",
    ),
    "ankle_breaker": BadgeDefinition(
        "Ankle Breaker", BadgeCategory.PLAYMAKING,
        "Increased chance of causing defender to stumble on dribble moves.",
    ),
    "bail_out": BadgeDefinition(
        "Bail Out", BadgeCategory.PLAYMAKING,
        "Improved passing accuracy when under pressure or in the air.",
    ),
    "lob_city_passer": BadgeDefinition(
        "Lob City Passer", BadgeCategory.PLAYMAKING,
        "Improved alley-oop pass accuracy and frequency.",
    ),

    # Defense badges
    "clamps": BadgeDefinition(
        "Clamps", BadgeCategory.DEFENSE,
        "Improved on-ball defense and cut-off ability.",
    ),
    "interceptor": BadgeDefinition(
        "Interceptor", BadgeCategory.DEFENSE,
        "Increased steal chance on passing lanes.",
    ),
    "intimidator": BadgeDefinition(
        "Intimidator", BadgeCategory.DEFENSE,
        "Reduces opponent's shot percentage when nearby.",
    ),
    "rim_protector": BadgeDefinition(
        "Rim Protector", BadgeCategory.DEFENSE,
        "Boost to blocks and shot contest at the rim.",
    ),
    "pick_dodger": BadgeDefinition(
        "Pick Dodger", BadgeCategory.DEFENSE,
        "Improved ability to navigate around screens.",
    ),
    "chase_down_artist": BadgeDefinition(
        "Chase Down Artist", BadgeCategory.DEFENSE,
        "Increased chase-down block frequency from behind.",
    ),
    "defensive_leader": BadgeDefinition(
        "Defensive Leader", BadgeCategory.DEFENSE,
        "Boosts teammates' defensive attributes when on the court.",
    ),

    # Rebounding badges
    "rebound_chaser": BadgeDefinition(
        "Rebound Chaser", BadgeCategory.REBOUNDING,
        "Improved ability to track and grab rebounds from distance.",
    ),
    "box_out_beast": BadgeDefinition(
        "Box Out Beast", BadgeCategory.REBOUNDING,
        "Improved box-out strength and positioning.",
    ),
    "worm": BadgeDefinition(
        "Worm", BadgeCategory.REBOUNDING,
        "Ability to swim around box-outs for offensive rebounds.",
    ),

    # Mental badges
    "clutch_performer": BadgeDefinition(
        "Clutch Performer", BadgeCategory.MENTAL,
        "Reduced pressure penalty in clutch situations.",
    ),
    "microwave": BadgeDefinition(
        "Microwave", BadgeCategory.MENTAL,
        "Gets hot faster; needs fewer consecutive makes to enter hot streak.",
    ),
    "alpha_dog": BadgeDefinition(
        "Alpha Dog", BadgeCategory.MENTAL,
        "Performance boost when team needs a leader; slight ego effect.",
    ),
}


@dataclass
class PlayerBadges:
    """A player's badge loadout.

    Maps badge keys to their tier level.
    """

    badges: Dict[str, BadgeTier] = field(default_factory=dict)

    def has_badge(self, badge_key: str) -> bool:
        """Check if the player has a specific badge."""
        return badge_key in self.badges

    def get_tier(self, badge_key: str) -> Optional[BadgeTier]:
        """Get the tier of a badge, or None if not owned."""
        return self.badges.get(badge_key)

    def tier_value(self, badge_key: str) -> int:
        """Get the numeric tier value (0 if not owned, 1-4 if owned)."""
        tier = self.badges.get(badge_key)
        return int(tier) if tier is not None else 0

    def tier_multiplier(self, badge_key: str) -> float:
        """Get a multiplier based on badge tier.

        Returns 1.0 (no badge), 1.02 (bronze), 1.04 (silver),
        1.06 (gold), 1.10 (HOF).
        """
        tier = self.tier_value(badge_key)
        return {0: 1.0, 1: 1.02, 2: 1.04, 3: 1.06, 4: 1.10}[tier]

    def add_badge(self, badge_key: str, tier: BadgeTier) -> None:
        """Add or upgrade a badge."""
        if badge_key not in BADGE_DEFINITIONS:
            raise ValueError(f"Unknown badge: {badge_key}")
        self.badges[badge_key] = tier

    def remove_badge(self, badge_key: str) -> None:
        """Remove a badge."""
        self.badges.pop(badge_key, None)

    def upgrade_badge(self, badge_key: str) -> bool:
        """Upgrade a badge by one tier. Returns False if already HOF or not owned."""
        current = self.badges.get(badge_key)
        if current is None or current == BadgeTier.HALL_OF_FAME:
            return False
        self.badges[badge_key] = BadgeTier(int(current) + 1)
        return True

    def badges_in_category(self, category: BadgeCategory) -> List[str]:
        """Get all badge keys in a specific category that this player has."""
        return [
            key for key in self.badges
            if key in BADGE_DEFINITIONS and BADGE_DEFINITIONS[key].category == category
        ]

    def count(self) -> int:
        """Total number of badges."""
        return len(self.badges)

    def total_tier_points(self) -> int:
        """Sum of all badge tier values (for comparison/ranking)."""
        return sum(int(t) for t in self.badges.values())
