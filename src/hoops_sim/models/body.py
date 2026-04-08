"""Physical body model for players."""

from __future__ import annotations

import enum
from dataclasses import dataclass


class Handedness(enum.Enum):
    """Dominant hand."""

    RIGHT = "right"
    LEFT = "left"
    AMBIDEXTROUS = "ambidextrous"


class HandSize(enum.Enum):
    """Hand size category (affects ball handling, palming, rebounding grip)."""

    SMALL = "small"
    AVERAGE = "average"
    LARGE = "large"
    EXTRA_LARGE = "extra_large"


@dataclass
class PlayerBody:
    """Physical body measurements and traits.

    All measurements use the standard NBA combine format.

    Attributes:
        height_inches: Height in inches (e.g., 78 = 6'6").
        weight_lbs: Weight in pounds.
        wingspan_inches: Wingspan in inches (fingertip to fingertip).
        standing_reach_inches: Standing reach in inches (flat-footed reach above head).
        body_fat_pct: Body fat percentage (affects speed/stamina tradeoffs).
        hand_size: Hand size category.
        handedness: Dominant hand.
        shoe_size: Shoe size (flavor stat, minor traction effect).
    """

    height_inches: int = 78  # 6'6"
    weight_lbs: int = 210
    wingspan_inches: int = 82
    standing_reach_inches: int = 104
    body_fat_pct: float = 8.0
    hand_size: HandSize = HandSize.AVERAGE
    handedness: Handedness = Handedness.RIGHT
    shoe_size: float = 14.0

    @property
    def height_feet(self) -> float:
        """Height in feet."""
        return self.height_inches / 12.0

    @property
    def height_display(self) -> str:
        """Height as a string like 6'6\"."""
        feet = self.height_inches // 12
        inches = self.height_inches % 12
        return f"{feet}'{inches}\""

    @property
    def wingspan_to_height_ratio(self) -> float:
        """Wingspan-to-height ratio. >1.0 means longer arms relative to height."""
        if self.height_inches == 0:
            return 1.0
        return self.wingspan_inches / self.height_inches

    @property
    def bmi(self) -> float:
        """Body mass index (weight_lbs / height_inches^2 * 703)."""
        if self.height_inches == 0:
            return 0.0
        return self.weight_lbs / (self.height_inches ** 2) * 703.0

    def is_undersized_for_position(self, typical_height_min: int) -> bool:
        """Check if the player is undersized for their position."""
        return self.height_inches < typical_height_min

    def is_long_for_height(self) -> bool:
        """Check if wingspan is notably longer than height (+4 inches or more)."""
        return self.wingspan_inches >= self.height_inches + 4

    def strength_modifier(self) -> float:
        """Weight-based modifier for contact situations.

        Heavier players have an advantage in post play, boxing out, and screens.
        Returns a multiplier centered around 1.0 for a 210-lb player.
        """
        return self.weight_lbs / 210.0
