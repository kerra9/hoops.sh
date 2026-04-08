"""Ball state, trajectory, and bounce physics."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field

from hoops_sim.physics.vec import Vec3
from hoops_sim.utils.constants import (
    BALL_AIR_DRAG,
    BALL_COEFFICIENT_OF_RESTITUTION,
    BALL_MASS,
    BALL_RADIUS,
    GRAVITY,
)


class BallState(enum.Enum):
    """Current state of the basketball."""

    HELD = "held"
    DRIBBLED = "dribbled"
    IN_FLIGHT_PASS = "in_flight_pass"
    IN_FLIGHT_SHOT = "in_flight_shot"
    LOOSE = "loose"
    DEAD = "dead"


@dataclass
class Ball:
    """Physical basketball with position, velocity, and spin."""

    position: Vec3 = field(default_factory=Vec3.zero)
    velocity: Vec3 = field(default_factory=Vec3.zero)
    spin: Vec3 = field(default_factory=Vec3.zero)  # backspin (x), sidespin (y), topspin (z) in RPM
    state: BallState = BallState.DEAD

    # Physical constants
    RADIUS: float = BALL_RADIUS
    MASS: float = BALL_MASS
    COR: float = BALL_COEFFICIENT_OF_RESTITUTION
    AIR_DRAG: float = BALL_AIR_DRAG

    def update_flight(self, dt: float) -> None:
        """Update ball position during flight (shot or pass).

        Applies gravity, air drag, and updates position from velocity.
        Called every tick (or sub-tick) while ball is in the air.

        Args:
            dt: Time step in seconds.
        """
        if self.state not in (BallState.IN_FLIGHT_SHOT, BallState.IN_FLIGHT_PASS, BallState.LOOSE):
            return

        # Air drag: opposes velocity, proportional to speed squared
        speed = self.velocity.magnitude()
        if speed > 0.01:
            drag_magnitude = self.AIR_DRAG * speed * speed
            drag_direction = self.velocity.normalized()
            drag_force = drag_direction * (-drag_magnitude)
            self.velocity += drag_force * dt

        # Gravity: only affects z component
        self.velocity.z -= GRAVITY * dt

        # Update position
        self.position += self.velocity * dt

    def bounce_off_floor(self) -> None:
        """Handle ball bouncing off the court floor.

        Reverses z-velocity with energy loss from coefficient of restitution.
        """
        if self.position.z <= self.RADIUS:
            self.position.z = self.RADIUS
            self.velocity.z = -self.velocity.z * self.COR
            # Friction reduces horizontal velocity on bounce
            self.velocity.x *= 0.9
            self.velocity.y *= 0.9

    def is_airborne(self) -> bool:
        """Check if the ball is above the floor."""
        return self.position.z > self.RADIUS + 0.01

    def set_held(self, holder_position: Vec3) -> None:
        """Ball is now held by a player."""
        self.position = holder_position.copy()
        self.velocity = Vec3.zero()
        self.spin = Vec3.zero()
        self.state = BallState.HELD

    def set_dribbled(self) -> None:
        """Ball is being dribbled."""
        self.state = BallState.DRIBBLED

    def launch_shot(self, velocity: Vec3, spin: Vec3) -> None:
        """Launch the ball as a shot."""
        self.velocity = velocity.copy()
        self.spin = spin.copy()
        self.state = BallState.IN_FLIGHT_SHOT

    def launch_pass(self, velocity: Vec3) -> None:
        """Launch the ball as a pass."""
        self.velocity = velocity.copy()
        self.spin = Vec3.zero()
        self.state = BallState.IN_FLIGHT_PASS

    def make_loose(self) -> None:
        """Ball becomes loose (turnover, deflection, etc.)."""
        self.state = BallState.LOOSE

    def make_dead(self) -> None:
        """Ball becomes dead (whistle, out of bounds, etc.)."""
        self.state = BallState.DEAD
        self.velocity = Vec3.zero()
