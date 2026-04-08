"""Contact detection and force calculation between players."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional

from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.constants import (
    CONTACT_HARD_THRESHOLD,
    CONTACT_INCIDENTAL_THRESHOLD,
    CONTACT_LIGHT_THRESHOLD,
    CONTACT_MODERATE_THRESHOLD,
)


class ContactType(enum.Enum):
    """Body part involved in contact."""

    BODY = "body"
    ARM = "arm"
    HAND = "hand"
    HIP = "hip"
    SHOULDER = "shoulder"
    LEG = "leg"


class ContactSeverity(enum.Enum):
    """How severe the contact is."""

    NONE = "none"
    INCIDENTAL = "incidental"  # No effect on play
    LIGHT = "light"  # May cause slight accuracy reduction
    MODERATE = "moderate"  # Affects shot trajectory; possible foul
    HARD = "hard"  # Likely foul; may affect balance
    FLAGRANT = "flagrant"  # Almost certain foul; injury risk


def classify_severity(severity_value: float) -> ContactSeverity:
    """Classify a numeric severity value into a ContactSeverity level."""
    if severity_value < CONTACT_INCIDENTAL_THRESHOLD:
        return ContactSeverity.NONE
    if severity_value < CONTACT_LIGHT_THRESHOLD:
        return ContactSeverity.INCIDENTAL
    if severity_value < CONTACT_MODERATE_THRESHOLD:
        return ContactSeverity.LIGHT
    if severity_value < CONTACT_HARD_THRESHOLD:
        return ContactSeverity.MODERATE
    if severity_value < 0.9:
        return ContactSeverity.HARD
    return ContactSeverity.FLAGRANT


@dataclass
class ContactEvent:
    """A contact event between two players.

    Attributes:
        offensive_position: Position of the offensive player.
        defensive_position: Position of the defensive player.
        offensive_velocity: Velocity of the offensive player.
        defensive_velocity: Velocity of the defensive player.
        offensive_weight: Weight of the offensive player in lbs.
        defensive_weight: Weight of the defensive player in lbs.
        defensive_set: Was the defender stationary (charge vs block)?
        defensive_legal_position: Was the defender in legal guarding position?
        contact_type: Body part involved.
        severity_value: Raw severity (0-1).
    """

    offensive_position: Vec2
    defensive_position: Vec2
    offensive_velocity: Vec2
    defensive_velocity: Vec2
    offensive_weight: float
    defensive_weight: float
    defensive_set: bool
    defensive_legal_position: bool
    contact_type: ContactType
    severity_value: float

    @property
    def contact_point(self) -> Vec2:
        """Midpoint between the two players at contact."""
        return self.offensive_position.lerp(self.defensive_position, 0.5)

    @property
    def relative_velocity(self) -> float:
        """How fast the players are moving relative to each other."""
        return (self.offensive_velocity - self.defensive_velocity).magnitude()

    @property
    def offensive_momentum(self) -> float:
        """Momentum of the offensive player (mass * speed)."""
        return self.offensive_weight * self.offensive_velocity.magnitude()

    @property
    def force(self) -> float:
        """Contact force in arbitrary units.

        Based on relative velocity and combined weight of both players.
        """
        return self.relative_velocity * (
            self.offensive_weight * 0.4 + self.defensive_weight * 0.4
        ) / 100.0

    @property
    def severity(self) -> ContactSeverity:
        """Classified severity level of the contact."""
        return classify_severity(self.severity_value)


def detect_contact(
    off_pos: Vec2,
    off_vel: Vec2,
    off_weight: float,
    def_pos: Vec2,
    def_vel: Vec2,
    def_weight: float,
    contact_radius: float = 2.5,
) -> Optional[ContactEvent]:
    """Detect if two players are in contact.

    Players are in contact when their positions overlap within the contact
    radius (roughly the combined body width).

    Args:
        off_pos: Offensive player position.
        off_vel: Offensive player velocity.
        off_weight: Offensive player weight in lbs.
        def_pos: Defensive player position.
        def_vel: Defensive player velocity.
        def_weight: Defensive player weight in lbs.
        contact_radius: Maximum distance for contact (feet).

    Returns:
        ContactEvent if contact occurs, None otherwise.
    """
    distance = off_pos.distance_to(def_pos)
    if distance > contact_radius:
        return None

    # Calculate severity based on closing speed and proximity
    relative_vel = (off_vel - def_vel).magnitude()
    proximity_factor = 1.0 - (distance / contact_radius)  # 0 at edge, 1 at overlap
    speed_factor = min(1.0, relative_vel / 20.0)  # Normalize to ~20 ft/s max

    severity = proximity_factor * 0.5 + speed_factor * 0.5

    # Determine if defender was set (stationary)
    defensive_set = def_vel.magnitude() < 1.0  # Nearly stationary

    # Legal guarding position: defender was set and facing the offensive player
    defensive_legal = defensive_set and proximity_factor > 0.3

    # Determine contact type based on relative angle and positions
    contact_type = _determine_contact_type(off_pos, def_pos, off_vel)

    return ContactEvent(
        offensive_position=off_pos,
        defensive_position=def_pos,
        offensive_velocity=off_vel,
        defensive_velocity=def_vel,
        offensive_weight=off_weight,
        defensive_weight=def_weight,
        defensive_set=defensive_set,
        defensive_legal_position=defensive_legal,
        contact_type=contact_type,
        severity_value=severity,
    )


def _determine_contact_type(
    off_pos: Vec2,
    def_pos: Vec2,
    off_vel: Vec2,
) -> ContactType:
    """Determine the type of contact based on positions and movement.

    Simplified model: uses the angle of approach to guess the contact type.
    """
    # Direction from defender to offensive player
    direction = off_pos - def_pos
    # Direction the offensive player is moving
    movement = off_vel.normalized() if off_vel.magnitude() > 0.1 else direction.normalized()

    # Angle between the approach and the connection line
    dot = direction.normalized().dot(movement)

    if dot > 0.7:
        return ContactType.BODY  # Head-on collision
    if dot > 0.3:
        return ContactType.SHOULDER  # Angled contact
    if dot > -0.3:
        return ContactType.HIP  # Side contact
    return ContactType.ARM  # Reaching / trailing contact
