"""Player movement physics: acceleration, deceleration, and momentum."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Dict

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    BACKPEDAL_SPEED_RATIO,
    DECELERATION_MULTIPLIER,
    ENERGY_DRAIN_JOG,
    ENERGY_DRAIN_SPRINT,
    ENERGY_DRAIN_STAND,
    ENERGY_DRAIN_WALK,
    LATERAL_SPEED_RATIO,
    MAX_ACCELERATION,
    MAX_SPRINT_SPEED,
    MIN_ACCELERATION,
    MIN_SPRINT_SPEED,
)
from hoops_sim.utils.math import attribute_to_range


class MovementType(enum.Enum):
    """Types of player movement."""

    STAND = "stand"
    WALK = "walk"
    JOG = "jog"
    SPRINT = "sprint"
    BACKPEDAL = "backpedal"
    LATERAL = "lateral"


# Speed fractions for each movement type (relative to max sprint speed)
_MOVEMENT_SPEED_FRACTION: Dict[MovementType, float] = {
    MovementType.STAND: 0.0,
    MovementType.WALK: 0.25,
    MovementType.JOG: 0.55,
    MovementType.SPRINT: 1.0,
    MovementType.BACKPEDAL: BACKPEDAL_SPEED_RATIO,
    MovementType.LATERAL: LATERAL_SPEED_RATIO,
}

# Energy drain per tick for each movement type
_MOVEMENT_ENERGY_DRAIN: Dict[MovementType, float] = {
    MovementType.STAND: ENERGY_DRAIN_STAND,
    MovementType.WALK: ENERGY_DRAIN_WALK,
    MovementType.JOG: ENERGY_DRAIN_JOG,
    MovementType.SPRINT: ENERGY_DRAIN_SPRINT,
    MovementType.BACKPEDAL: ENERGY_DRAIN_JOG * 1.2,  # Backpedaling is slightly more tiring
    MovementType.LATERAL: ENERGY_DRAIN_JOG * 1.1,
}


@dataclass
class PlayerKinematics:
    """Physics-based movement model for a player.

    Each player has position, velocity, facing angle, and movement parameters
    derived from their attributes (speed, acceleration, agility, etc.).

    Attributes:
        position: Current 2D position on the court.
        velocity: Current velocity vector.
        facing_angle: Direction the player is facing (degrees, 0 = right).
        max_sprint_speed: Top speed in ft/s (from speed attribute).
        acceleration: Acceleration rate in ft/s^2 (from acceleration attribute).
        deceleration: Braking rate in ft/s^2.
        lateral_speed: Maximum lateral movement speed in ft/s (from lateral quickness).
    """

    position: Vec2
    velocity: Vec2
    facing_angle: float

    # Movement parameters (derived from attributes)
    max_sprint_speed: float
    acceleration: float
    deceleration: float
    lateral_speed: float

    @staticmethod
    def from_attributes(
        position: Vec2,
        speed_attr: int,
        acceleration_attr: int,
        lateral_quickness_attr: int,
    ) -> PlayerKinematics:
        """Create a PlayerKinematics from player attribute ratings.

        Args:
            position: Starting position.
            speed_attr: Speed rating (0-99).
            acceleration_attr: Acceleration rating (0-99).
            lateral_quickness_attr: Lateral quickness rating (0-99).

        Returns:
            Configured PlayerKinematics.
        """
        max_speed = attribute_to_range(speed_attr, MIN_SPRINT_SPEED, MAX_SPRINT_SPEED)
        accel = attribute_to_range(acceleration_attr, MIN_ACCELERATION, MAX_ACCELERATION)
        lat_speed = max_speed * attribute_to_range(lateral_quickness_attr, 0.60, 0.85)

        return PlayerKinematics(
            position=position.copy(),
            velocity=Vec2.zero(),
            facing_angle=0.0,
            max_sprint_speed=max_speed,
            acceleration=accel,
            deceleration=accel * DECELERATION_MULTIPLIER,
            lateral_speed=lat_speed,
        )

    def get_speed_for_type(self, movement_type: MovementType) -> float:
        """Get the target speed for a given movement type."""
        fraction = _MOVEMENT_SPEED_FRACTION[movement_type]
        if movement_type == MovementType.LATERAL:
            return self.lateral_speed
        return self.max_sprint_speed * fraction

    def update(
        self,
        dt: float,
        target_position: Vec2,
        movement_type: MovementType,
    ) -> float:
        """Update position based on movement physics.

        Applies acceleration/deceleration toward the target speed,
        then updates position from velocity.

        Args:
            dt: Time step in seconds.
            target_position: Where the player is trying to move to.
            movement_type: How the player is moving.

        Returns:
            Energy cost for this tick of movement.
        """
        if movement_type == MovementType.STAND:
            # Decelerate to a stop
            current_speed = self.velocity.magnitude()
            if current_speed > 0.1:
                new_speed = max(0.0, current_speed - self.deceleration * dt)
                self.velocity = self.velocity.normalized() * new_speed
            else:
                self.velocity = Vec2.zero()
            self.position += self.velocity * dt
            return _MOVEMENT_ENERGY_DRAIN[MovementType.STAND]

        # Direction toward target
        diff = target_position - self.position
        distance = diff.magnitude()
        if distance < 0.1:
            # Already at target, stop
            self.velocity = Vec2.zero()
            return _MOVEMENT_ENERGY_DRAIN[MovementType.STAND]

        direction = diff.normalized()
        desired_speed = self.get_speed_for_type(movement_type)

        # Acceleration model: can't instantly reach top speed
        current_speed = self.velocity.magnitude()
        if current_speed < desired_speed:
            new_speed = min(current_speed + self.acceleration * dt, desired_speed)
        else:
            new_speed = max(current_speed - self.deceleration * dt, desired_speed)

        # Should we slow down as we approach the target?
        # Calculate stopping distance: v^2 / (2 * deceleration)
        stopping_distance = (new_speed * new_speed) / (2.0 * self.deceleration) if self.deceleration > 0 else 0
        if distance < stopping_distance:
            # Start decelerating
            new_speed = max(0.0, new_speed - self.deceleration * dt)

        self.velocity = direction * new_speed
        self.position += self.velocity * dt

        # Update facing angle toward movement direction
        if new_speed > 0.5:
            self.facing_angle = direction.angle()

        # Energy cost is proportional to effort
        speed_ratio = new_speed / self.max_sprint_speed if self.max_sprint_speed > 0 else 0
        energy_cost = _MOVEMENT_ENERGY_DRAIN[movement_type] * (0.5 + speed_ratio * 0.5)
        return energy_cost

    def current_speed(self) -> float:
        """Current speed in ft/s."""
        return self.velocity.magnitude()

    def is_moving(self) -> bool:
        """Whether the player is currently moving."""
        return self.velocity.magnitude_squared() > 0.01
