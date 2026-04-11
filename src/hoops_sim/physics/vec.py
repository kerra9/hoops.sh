"""Vec2 and Vec3 math utilities for spatial calculations."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Vec2:
    """2D vector for court positions and movements."""

    x: float = 0.0
    y: float = 0.0

    # -- Arithmetic ----------------------------------------------------------

    def __add__(self, other: Vec2) -> Vec2:
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2) -> Vec2:
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float) -> Vec2:
        return Vec2(self.x * scalar, self.y * scalar)

    def __rmul__(self, scalar: float) -> Vec2:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vec2:
        if abs(scalar) < 1e-10:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / scalar, self.y / scalar)

    def __neg__(self) -> Vec2:
        return Vec2(-self.x, -self.y)

    def __iadd__(self, other: Vec2) -> Vec2:
        self.x += other.x
        self.y += other.y
        return self

    def __isub__(self, other: Vec2) -> Vec2:
        self.x -= other.x
        self.y -= other.y
        return self

    def __imul__(self, scalar: float) -> Vec2:
        self.x *= scalar
        self.y *= scalar
        return self

    # -- Properties -----------------------------------------------------------

    def magnitude(self) -> float:
        """Length of the vector."""
        return math.hypot(self.x, self.y)

    def magnitude_squared(self) -> float:
        """Squared length (avoids sqrt for comparisons)."""
        return self.x * self.x + self.y * self.y

    def normalized(self) -> Vec2:
        """Unit vector in the same direction. Returns zero vector if magnitude is ~0."""
        mag = self.magnitude()
        if mag < 1e-10:
            return Vec2(0.0, 0.0)
        return Vec2(self.x / mag, self.y / mag)

    def dot(self, other: Vec2) -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y

    def cross(self, other: Vec2) -> float:
        """2D cross product (scalar: z-component of the 3D cross product)."""
        return self.x * other.y - self.y * other.x

    def angle(self) -> float:
        """Angle in degrees from positive x-axis, in range [0, 360)."""
        rad = math.atan2(self.y, self.x)
        deg = math.degrees(rad)
        return deg % 360.0

    def angle_to(self, other: Vec2) -> float:
        """Angle in degrees from this vector to another."""
        delta = other - self
        return delta.angle()

    def distance_to(self, other: Vec2) -> float:
        """Euclidean distance to another point."""
        return (other - self).magnitude()

    def rotate(self, degrees: float) -> Vec2:
        """Rotate the vector by the given angle in degrees."""
        rad = math.radians(degrees)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)
        return Vec2(
            self.x * cos_a - self.y * sin_a,
            self.x * sin_a + self.y * cos_a,
        )

    def lerp(self, other: Vec2, t: float) -> Vec2:
        """Linear interpolation toward another vector."""
        t = max(0.0, min(1.0, t))
        return Vec2(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
        )

    def copy(self) -> Vec2:
        """Return a copy of this vector."""
        return Vec2(self.x, self.y)

    @staticmethod
    def from_angle(degrees: float, magnitude: float = 1.0) -> Vec2:
        """Create a vector from an angle (degrees) and magnitude."""
        rad = math.radians(degrees)
        return Vec2(math.cos(rad) * magnitude, math.sin(rad) * magnitude)

    @staticmethod
    def zero() -> Vec2:
        return Vec2(0.0, 0.0)


@dataclass
class Vec3:
    """3D vector for ball physics (z = height above court)."""

    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # -- Arithmetic ----------------------------------------------------------

    def __add__(self, other: Vec3) -> Vec3:
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vec3) -> Vec3:
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float) -> Vec3:
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def __rmul__(self, scalar: float) -> Vec3:
        return self.__mul__(scalar)

    def __truediv__(self, scalar: float) -> Vec3:
        if abs(scalar) < 1e-10:
            return Vec3(0.0, 0.0, 0.0)
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __neg__(self) -> Vec3:
        return Vec3(-self.x, -self.y, -self.z)

    def __iadd__(self, other: Vec3) -> Vec3:
        self.x += other.x
        self.y += other.y
        self.z += other.z
        return self

    def __isub__(self, other: Vec3) -> Vec3:
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        return self

    def __imul__(self, scalar: float) -> Vec3:
        self.x *= scalar
        self.y *= scalar
        self.z *= scalar
        return self

    # -- Properties -----------------------------------------------------------

    def magnitude(self) -> float:
        """Length of the vector."""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)

    def magnitude_squared(self) -> float:
        """Squared length (avoids sqrt for comparisons)."""
        return self.x * self.x + self.y * self.y + self.z * self.z

    def normalized(self) -> Vec3:
        """Unit vector in the same direction."""
        mag = self.magnitude()
        if mag < 1e-10:
            return Vec3(0.0, 0.0, 0.0)
        return Vec3(self.x / mag, self.y / mag, self.z / mag)

    def dot(self, other: Vec3) -> float:
        """Dot product."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3) -> Vec3:
        """Cross product."""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )

    def distance_to(self, other: Vec3) -> float:
        """Euclidean distance to another point."""
        return (other - self).magnitude()

    def xy(self) -> Vec2:
        """Project onto the XY plane (court surface)."""
        return Vec2(self.x, self.y)

    def lerp(self, other: Vec3, t: float) -> Vec3:
        """Linear interpolation toward another vector."""
        t = max(0.0, min(1.0, t))
        return Vec3(
            self.x + (other.x - self.x) * t,
            self.y + (other.y - self.y) * t,
            self.z + (other.z - self.z) * t,
        )

    def copy(self) -> Vec3:
        """Return a copy of this vector."""
        return Vec3(self.x, self.y, self.z)

    @staticmethod
    def from_angle_and_speed(
        elevation_degrees: float,
        speed: float,
        heading_degrees: float,
    ) -> Vec3:
        """Create a velocity vector from elevation angle, speed, and heading.

        Args:
            elevation_degrees: Angle above horizontal (0 = flat, 90 = straight up).
            speed: Total speed magnitude in ft/s.
            heading_degrees: Horizontal direction in degrees (0 = positive x).

        Returns:
            Vec3 velocity with appropriate x, y, z components.
        """
        elev_rad = math.radians(elevation_degrees)
        head_rad = math.radians(heading_degrees)

        horizontal_speed = speed * math.cos(elev_rad)
        vertical_speed = speed * math.sin(elev_rad)

        return Vec3(
            horizontal_speed * math.cos(head_rad),
            horizontal_speed * math.sin(head_rad),
            vertical_speed,
        )

    @staticmethod
    def zero() -> Vec3:
        return Vec3(0.0, 0.0, 0.0)


def distance_2d(a: Vec2 | Vec3, b: Vec2 | Vec3) -> float:
    """2D distance between two points (ignoring z if Vec3)."""
    ax = a.x
    ay = a.y
    bx = b.x
    by = b.y
    return math.hypot(bx - ax, by - ay)
