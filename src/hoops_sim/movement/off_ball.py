"""Off-ball movement: cuts, flares, curls, pops, drifts, spot-up relocation."""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2


class OffBallAction(enum.Enum):
    """Types of off-ball movement."""

    STAND = "stand"  # Stay in position
    SPOT_UP = "spot_up"  # Relocate to an open spot
    BASKET_CUT = "basket_cut"  # Cut toward the basket
    BACKDOOR_CUT = "backdoor_cut"  # Cut behind the defender to the basket
    FLARE = "flare"  # Move away from the ball to the wing/corner
    CURL = "curl"  # Curl around a screen toward the ball
    POP = "pop"  # Pop out to the perimeter (typically after screening)
    DRIFT = "drift"  # Drift to an open area on the perimeter
    FILL = "fill"  # Fill a vacated spot in the offense
    RELOCATE = "relocate"  # Move to a new 3-point spot
    CRASH = "crash"  # Crash the boards for an offensive rebound
    LEAK = "leak"  # Leak out for a fast break


@dataclass
class OffBallMovement:
    """A planned off-ball movement."""

    action: OffBallAction
    target_position: Vec2
    urgency: float = 0.5  # 0-1


def calculate_spot_up_position(
    ball_position: Vec2,
    current_position: Vec2,
    basket_position: Vec2,
    is_shooter: bool,
) -> Vec2:
    """Calculate ideal spot-up position for spacing.

    Shooters spread to the three-point line; non-shooters position
    in the mid-range or near the basket.

    Args:
        ball_position: Current ball position.
        current_position: Player's current position.
        basket_position: The basket being attacked.
        is_shooter: Whether this player is a perimeter shooter.

    Returns:
        Target position for spot-up.
    """
    # Direction from basket to player (radial positioning)
    direction = current_position - basket_position
    if direction.magnitude() < 0.1:
        direction = Vec2(1.0, 0.0)
    direction = direction.normalized()

    if is_shooter:
        # Position on the three-point arc (~24 feet from basket)
        return basket_position + direction * 24.0
    else:
        # Position in the mid-range or paint (~12 feet)
        return basket_position + direction * 12.0


def calculate_cut_target(
    basket_position: Vec2,
    defender_position: Vec2,
    cut_type: OffBallAction,
) -> Vec2:
    """Calculate the target for a cutting action.

    Args:
        basket_position: The basket being attacked.
        defender_position: Position of the player's defender.
        cut_type: Type of cut.

    Returns:
        Target position for the cut.
    """
    if cut_type == OffBallAction.BASKET_CUT:
        # Cut straight to the basket
        return basket_position.copy()

    if cut_type == OffBallAction.BACKDOOR_CUT:
        # Cut behind the defender toward the basket
        def_to_basket = basket_position - defender_position
        if def_to_basket.magnitude() < 0.1:
            return basket_position.copy()
        offset = def_to_basket.normalized().rotate(30) * 3.0
        return basket_position + offset

    if cut_type == OffBallAction.FLARE:
        # Move away from the ball, toward the wing
        away = (defender_position - basket_position).normalized()
        return basket_position + away * 22.0

    # Default: move toward basket
    return basket_position.copy()
