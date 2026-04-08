"""Player attributes: 60+ ratings across all skill categories."""

from __future__ import annotations

from dataclasses import dataclass, field, fields
from typing import Dict, Iterator, Tuple


def _attr(default: int = 50) -> int:
    """Default attribute value factory."""
    return default


@dataclass
class ShootingAttributes:
    """Shooting skill ratings (0-99)."""

    close_shot: int = 50
    mid_range: int = 50
    three_point: int = 50
    free_throw: int = 50
    shot_iq: int = 50
    shot_consistency: int = 50
    shot_speed: int = 50  # Release speed (affects blockability)


@dataclass
class FinishingAttributes:
    """Finishing at the rim ratings (0-99)."""

    layup: int = 50
    standing_dunk: int = 50
    driving_dunk: int = 50
    draw_foul: int = 50
    acrobatic_finish: int = 50  # Euro-step, reverse layup, finger roll
    post_hook: int = 50
    post_fadeaway: int = 50
    post_moves: int = 50


@dataclass
class PlaymakingAttributes:
    """Playmaking and ball handling ratings (0-99)."""

    ball_handle: int = 50
    pass_accuracy: int = 50
    pass_vision: int = 50
    pass_iq: int = 50
    speed_with_ball: int = 50
    hands: int = 50  # Catching passes, securing rebounds


@dataclass
class DefensiveAttributes:
    """Defensive skill ratings (0-99)."""

    interior_defense: int = 50
    perimeter_defense: int = 50
    lateral_quickness: int = 50
    steal: int = 50
    block: int = 50
    defensive_iq: int = 50
    defensive_consistency: int = 50
    pick_dodger: int = 50  # Navigating screens
    help_defense_iq: int = 50
    on_ball_defense: int = 50


@dataclass
class ReboundingAttributes:
    """Rebounding ratings (0-99)."""

    offensive_rebound: int = 50
    defensive_rebound: int = 50
    box_out: int = 50


@dataclass
class AthleticAttributes:
    """Athletic/physical ratings (0-99)."""

    speed: int = 50
    acceleration: int = 50
    vertical_leap: int = 50
    strength: int = 50
    stamina: int = 50
    hustle: int = 50
    durability: int = 50  # Injury resistance


@dataclass
class MentalAttributes:
    """Mental and intangible ratings (0-99)."""

    basketball_iq: int = 50
    clutch: int = 50
    composure: int = 50  # Performance under pressure / hostile crowds
    work_ethic: int = 50  # Affects development rate
    coachability: int = 50  # Affects scheme familiarity learning
    leadership: int = 50
    mentorship: int = 50  # Ability to help young players develop
    motor: int = 50  # Effort level consistency


@dataclass
class PlayerAttributes:
    """Complete set of player attributes organized by category.

    Contains 60+ individual ratings across 7 categories, each rated 0-99.
    """

    shooting: ShootingAttributes = field(default_factory=ShootingAttributes)
    finishing: FinishingAttributes = field(default_factory=FinishingAttributes)
    playmaking: PlaymakingAttributes = field(default_factory=PlaymakingAttributes)
    defense: DefensiveAttributes = field(default_factory=DefensiveAttributes)
    rebounding: ReboundingAttributes = field(default_factory=ReboundingAttributes)
    athleticism: AthleticAttributes = field(default_factory=AthleticAttributes)
    mental: MentalAttributes = field(default_factory=MentalAttributes)

    def overall(self) -> int:
        """Calculate an overall rating from all attributes.

        Uses a weighted average that values scoring and defense most.
        """
        weights = {
            'shooting': 0.18,
            'finishing': 0.14,
            'playmaking': 0.16,
            'defense': 0.18,
            'rebounding': 0.08,
            'athleticism': 0.14,
            'mental': 0.12,
        }
        total = 0.0
        for category_name, weight in weights.items():
            category = getattr(self, category_name)
            avg = _category_average(category)
            total += avg * weight
        return int(round(total))

    def iter_all(self) -> Iterator[Tuple[str, str, int]]:
        """Iterate over all attributes as (category, name, value) tuples."""
        for cat_field in fields(self):
            category = getattr(self, cat_field.name)
            for attr_field in fields(category):
                yield cat_field.name, attr_field.name, getattr(category, attr_field.name)

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        """Convert all attributes to a nested dictionary."""
        result: Dict[str, Dict[str, int]] = {}
        for cat_field in fields(self):
            category = getattr(self, cat_field.name)
            result[cat_field.name] = {}
            for attr_field in fields(category):
                result[cat_field.name][attr_field.name] = getattr(category, attr_field.name)
        return result

    def get(self, category: str, name: str) -> int:
        """Get a specific attribute value by category and name."""
        cat = getattr(self, category, None)
        if cat is None:
            raise ValueError(f"Unknown category: {category}")
        val = getattr(cat, name, None)
        if val is None:
            raise ValueError(f"Unknown attribute: {category}.{name}")
        return val

    def count(self) -> int:
        """Total number of individual attributes."""
        return sum(1 for _ in self.iter_all())


def _category_average(category: object) -> float:
    """Average all int fields in a dataclass."""
    vals = [getattr(category, f.name) for f in fields(category) if isinstance(getattr(category, f.name), int)]
    if not vals:
        return 0.0
    return sum(vals) / len(vals)
