"""Locomotion: walk, jog, sprint, backpedal with physics-based acceleration.

This module wraps PlayerKinematics with higher-level movement commands
that the AI and play system use.
"""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.physics.kinematics import MovementType, PlayerKinematics
from hoops_sim.physics.vec import Vec2


@dataclass
class MovementCommand:
    """A movement instruction for a player."""

    target: Vec2
    movement_type: MovementType
    priority: float = 0.5  # 0-1: how urgently the player should reach the target


def execute_movement(
    kinematics: PlayerKinematics,
    command: MovementCommand,
    dt: float,
) -> float:
    """Execute a movement command and return energy cost.

    Args:
        kinematics: The player's kinematics state.
        command: Movement instruction.
        dt: Time step in seconds.

    Returns:
        Energy cost for this tick.
    """
    return kinematics.update(dt, command.target, command.movement_type)


def choose_movement_type(
    current_pos: Vec2,
    target_pos: Vec2,
    is_defensive: bool,
    urgency: float,
) -> MovementType:
    """Choose the appropriate movement type based on context.

    Args:
        current_pos: Current position.
        target_pos: Target position.
        is_defensive: Whether the player is on defense.
        urgency: How urgently the player needs to move (0-1).

    Returns:
        The appropriate MovementType.
    """
    distance = current_pos.distance_to(target_pos)

    if distance < 1.0:
        return MovementType.STAND

    if is_defensive:
        if distance < 4.0:
            return MovementType.LATERAL
        if urgency > 0.7:
            return MovementType.SPRINT
        return MovementType.BACKPEDAL

    # Offensive movement
    if urgency > 0.8:
        return MovementType.SPRINT
    if distance > 15.0:
        return MovementType.SPRINT
    if distance > 6.0:
        return MovementType.JOG
    return MovementType.WALK
