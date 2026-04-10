"""Screen mechanics: setting screens, quality, legality, and off-ball screens.

Screens are physical events that create advantages. The screener plants,
the ball handler uses the screen, and the defense must react. Screen quality
depends on the screener's size, strength, and positioning.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


class ScreenType(enum.Enum):
    """Types of screens."""

    BALL_SCREEN = "ball_screen"  # PnR / PnP
    PIN_DOWN = "pin_down"  # Screen for shooter coming to perimeter
    FLARE_SCREEN = "flare_screen"  # Screen freeing shooter away from ball
    BACK_SCREEN = "back_screen"  # Screen freeing cutter to basket
    STAGGER = "stagger"  # Two consecutive screens
    CROSS_SCREEN = "cross_screen"  # Screen in the post area
    DOWN_SCREEN = "down_screen"  # Screen toward baseline


@dataclass
class ScreenResult:
    """Result of a screen action."""

    screen_type: ScreenType
    quality: float = 0.5  # 0-1, how effective the screen was
    is_legal: bool = True  # Whether the screen was legal (not moving)
    moving_screen_called: bool = False
    separation_created: float = 0.0  # Feet of separation for the user
    screener_position: Vec2 = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.screener_position is None:
            self.screener_position = Vec2(0.0, 0.0)


def evaluate_screen(
    screen_type: ScreenType,
    screener_strength: int,
    screener_weight: float,
    screener_screen_rating: int,
    defender_strength: int,
    defender_weight: float,
    is_stationary: bool,
    moving_screen_detection: float,
    rng: SeededRNG,
) -> ScreenResult:
    """Evaluate the quality and legality of a screen.

    Args:
        screen_type: Type of screen being set.
        screener_strength: Screener's strength attribute (0-99).
        screener_weight: Screener's weight in lbs.
        screener_screen_rating: Screener's screen-setting rating (0-99).
        defender_strength: Defender's strength (0-99).
        defender_weight: Defender's weight in lbs.
        is_stationary: Whether the screener was stationary when contact occurred.
        moving_screen_detection: Ref's moving screen detection rate (0-1).
        rng: Random number generator.

    Returns:
        ScreenResult with quality and legality.
    """
    # Screen quality from screener attributes
    base_quality = (
        screener_strength / 99.0 * 0.3
        + screener_weight / 280.0 * 0.3
        + screener_screen_rating / 99.0 * 0.4
    )

    # Defender's ability to fight through
    defender_resistance = (
        defender_strength / 99.0 * 0.4
        + defender_weight / 280.0 * 0.3
    )

    quality = base_quality - defender_resistance * 0.5
    quality = max(0.1, min(1.0, quality + rng.gauss(0, 0.1)))

    # Legality check
    is_legal = is_stationary
    moving_screen_called = False
    if not is_stationary:
        # Chance of moving screen being called
        call_chance = moving_screen_detection * 0.5
        if rng.random() < call_chance:
            moving_screen_called = True

    # Separation created depends on quality and screen type
    base_separation = quality * 3.0
    if screen_type == ScreenType.BALL_SCREEN:
        base_separation *= 1.2  # Ball screens create more space
    elif screen_type == ScreenType.BACK_SCREEN:
        base_separation *= 1.3  # Back screens catch defenders off guard
    elif screen_type == ScreenType.FLARE_SCREEN:
        base_separation *= 1.1

    separation = max(0.5, base_separation + rng.gauss(0, 0.5))

    return ScreenResult(
        screen_type=screen_type,
        quality=quality,
        is_legal=is_legal,
        moving_screen_called=moving_screen_called,
        separation_created=separation,
    )
