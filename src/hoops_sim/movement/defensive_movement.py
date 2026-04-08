"""Defensive movement: close-out, hedge, recover, rotate, help, scramble."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2


class DefensiveAction(enum.Enum):
    """Types of defensive movement."""

    GUARD_MAN = "guard_man"  # Stay with assigned man
    CLOSE_OUT = "close_out"  # Sprint to contest a shooter
    HELP = "help"  # Leave man to help on a drive
    RECOVER = "recover"  # Get back to assigned man after helping
    ROTATE = "rotate"  # Rotate to cover a teammate's man
    HEDGE = "hedge"  # Step out on a screen to slow the ball handler
    SCRAMBLE = "scramble"  # Chaotic recovery, find anyone to guard
    DROP = "drop"  # Drop back toward the paint (PnR coverage)
    SWITCH = "switch"  # Switch defensive assignment
    DENY = "deny"  # Deny the ball, overplay the passing lane


@dataclass
class DefensiveMovementCommand:
    """A defensive movement instruction."""

    action: DefensiveAction
    target_position: Vec2
    urgency: float = 0.5


def calculate_on_ball_position(
    offensive_player_pos: Vec2,
    basket_position: Vec2,
    gap: float = 4.0,
) -> Vec2:
    """Calculate ideal defensive position against the ball handler.

    The defender should be between the ball handler and the basket,
    at a comfortable gap distance.

    Args:
        offensive_player_pos: Ball handler's position.
        basket_position: The basket being defended.
        gap: Distance to maintain from the offensive player (feet).

    Returns:
        Target defensive position.
    """
    # Position between offensive player and basket
    direction = basket_position - offensive_player_pos
    if direction.magnitude() < 0.1:
        direction = Vec2(0.0, -1.0)
    direction = direction.normalized()
    return offensive_player_pos + direction * gap


def calculate_help_position(
    own_man_pos: Vec2,
    drive_pos: Vec2,
    basket_position: Vec2,
) -> Vec2:
    """Calculate position to help on a drive while staying aware of own man.

    The help defender positions between the driver and the basket,
    while staying close enough to recover to their assignment.

    Args:
        own_man_pos: Position of the player this defender is assigned to.
        drive_pos: Position of the player driving to the basket.
        basket_position: The basket being defended.

    Returns:
        Help defense position.
    """
    # Split the difference: closer to the driver but aware of own man
    drive_to_basket = basket_position - drive_pos
    if drive_to_basket.magnitude() < 0.1:
        return basket_position.copy()

    help_spot = drive_pos + drive_to_basket.normalized() * 5.0

    # Shade toward own man slightly so recovery is possible
    own_man_pull = (own_man_pos - help_spot) * 0.2
    return help_spot + own_man_pull


def calculate_closeout_position(
    shooter_pos: Vec2,
    current_pos: Vec2,
) -> Vec2:
    """Calculate close-out target: run at the shooter but under control.

    The defender sprints at the shooter but stops about 3 feet away
    to avoid fouling on a pump fake.

    Returns:
        Close-out target position.
    """
    direction = shooter_pos - current_pos
    if direction.magnitude() < 3.0:
        return current_pos.copy()  # Already close enough
    return shooter_pos - direction.normalized() * 3.0


def calculate_rotation_position(
    uncovered_player_pos: Vec2,
    basket_position: Vec2,
) -> Vec2:
    """Calculate position to rotate to when a teammate helps.

    Args:
        uncovered_player_pos: Position of the player left open by the helper.
        basket_position: The basket being defended.

    Returns:
        Rotation target position.
    """
    # Position between the uncovered player and the basket
    direction = basket_position - uncovered_player_pos
    if direction.magnitude() < 0.1:
        return basket_position.copy()
    return uncovered_player_pos + direction.normalized() * 5.0
