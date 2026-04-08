"""Shot trajectory calculation: parabolic arc with release point and spin."""

from __future__ import annotations

import math
from dataclasses import dataclass

from hoops_sim.physics.vec import Vec2, Vec3, distance_2d
from hoops_sim.utils.constants import (
    BASKET_HEIGHT,
    BASKET_X,
    BASKET_Y,
    GRAVITY,
    MAX_BACKSPIN_RPM,
    MIN_BACKSPIN_RPM,
    OPTIMAL_RELEASE_ANGLE_AT_RIM,
    OPTIMAL_RELEASE_ANGLE_MID,
    OPTIMAL_RELEASE_ANGLE_THREE,
    SHOT_ANGLE_VARIANCE_SCALE,
    SHOT_SPEED_VARIANCE_SCALE,
)
from typing import Optional

from hoops_sim.utils.rng import SeededRNG


BASKET_POSITION = Vec2(BASKET_X, BASKET_Y)


@dataclass
class ShotTrajectory:
    """Parameters of a shot in flight."""

    release_point: Vec3
    velocity: Vec3
    spin: Vec3  # backspin (x), sidespin (y), topspin (z) in RPM
    release_angle: float  # degrees above horizontal
    heading_angle: float  # horizontal direction in degrees


def optimal_release_angle(distance_to_basket: float) -> float:
    """Compute the optimal release angle based on distance to the basket.

    Closer shots use a higher arc; longer shots use a flatter arc.
    """
    if distance_to_basket <= 4.0:
        return OPTIMAL_RELEASE_ANGLE_AT_RIM
    if distance_to_basket >= 23.0:
        return OPTIMAL_RELEASE_ANGLE_THREE
    # Linear interpolation between rim and three-point
    t = (distance_to_basket - 4.0) / (23.0 - 4.0)
    return OPTIMAL_RELEASE_ANGLE_AT_RIM + t * (OPTIMAL_RELEASE_ANGLE_THREE - OPTIMAL_RELEASE_ANGLE_AT_RIM)


def required_launch_speed(
    distance: float,
    release_angle_deg: float,
    release_height: float,
    target_height: float = BASKET_HEIGHT,
) -> float:
    """Calculate the launch speed needed to reach the basket.

    Uses projectile motion equations to find the speed that lands the ball
    at (distance, target_height) given the release angle and height.

    Args:
        distance: Horizontal distance to the basket in feet.
        release_angle_deg: Release angle in degrees above horizontal.
        release_height: Height of the release point in feet.
        target_height: Height of the target (rim) in feet.

    Returns:
        Required launch speed in ft/s.
    """
    angle_rad = math.radians(release_angle_deg)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    delta_h = target_height - release_height

    # From projectile equations:
    # delta_h = distance * tan(angle) - (g * distance^2) / (2 * v^2 * cos^2(angle))
    # Solving for v^2:
    # v^2 = (g * distance^2) / (2 * cos^2(angle) * (distance * tan(angle) - delta_h))
    denominator = distance * sin_a / cos_a - delta_h
    if denominator <= 0:
        # The angle is too flat to reach the target height; use a fallback
        denominator = 0.1

    v_squared = (GRAVITY * distance * distance) / (2.0 * cos_a * cos_a * denominator)
    if v_squared <= 0:
        return 20.0  # Fallback minimum speed
    return math.sqrt(v_squared)


def calculate_shot_trajectory(
    shooter_position: Vec2,
    shooter_height_inches: float,
    standing_reach_inches: float,
    vertical_leap_inches: float,
    is_jump_shot: bool,
    zone_rating: int,
    shot_release_quality: float,
    rng: SeededRNG,
    basket_position: Optional[Vec2] = None,
) -> ShotTrajectory:
    """Calculate the full trajectory for a shot attempt.

    Args:
        shooter_position: 2D court position of the shooter.
        shooter_height_inches: Player height in inches.
        standing_reach_inches: Player standing reach in inches.
        vertical_leap_inches: Player vertical leap in inches.
        is_jump_shot: Whether the player is jumping.
        zone_rating: Shooting rating for this zone (0-99).
        shot_release_quality: Quality of the shot release timing (0.0-1.0).
        rng: Random number generator.
        basket_position: Override basket position (defaults to standard).

    Returns:
        A ShotTrajectory with release point, velocity, and spin.
    """
    target = basket_position or BASKET_POSITION

    # Release height: player height + reach extension + jump
    release_height = (
        shooter_height_inches / 12.0
        + standing_reach_inches / 12.0 * 0.4
        + (vertical_leap_inches / 12.0 * 0.7 if is_jump_shot else 0.0)
    )

    # Distance to basket
    distance = shooter_position.distance_to(target)

    # Heading angle (direction from shooter to basket)
    delta = target - shooter_position
    heading = delta.angle()

    # Optimal release angle
    opt_angle = optimal_release_angle(distance)

    # Variance based on skill: lower rating = more variance
    skill_deficit = 100 - zone_rating
    angle_variance = skill_deficit * SHOT_ANGLE_VARIANCE_SCALE
    speed_variance = skill_deficit * SHOT_SPEED_VARIANCE_SCALE

    # Release quality affects variance (perfect release = less variance)
    release_factor = 0.5 + shot_release_quality * 0.5  # 0.5 to 1.0
    angle_variance *= (2.0 - release_factor)
    speed_variance *= (2.0 - release_factor)

    # Actual release angle with noise
    actual_angle = opt_angle + rng.gauss(0, angle_variance)
    actual_angle = max(25.0, min(70.0, actual_angle))  # Clamp to reasonable range

    # Required speed and actual speed with noise
    req_speed = required_launch_speed(distance, actual_angle, release_height)
    actual_speed = req_speed * (1.0 + rng.gauss(0, speed_variance / 100.0))
    actual_speed = max(5.0, actual_speed)  # Minimum speed

    # Backspin: better shooters have more consistent spin
    base_backspin = MIN_BACKSPIN_RPM + (zone_rating / 100.0) * (MAX_BACKSPIN_RPM - MIN_BACKSPIN_RPM)
    backspin = base_backspin + rng.gauss(0, 15)
    sidespin = rng.gauss(0, 20)  # Small random sidespin

    # Build the velocity vector
    velocity = Vec3.from_angle_and_speed(actual_angle, actual_speed, heading)

    release_point = Vec3(shooter_position.x, shooter_position.y, release_height)
    spin = Vec3(backspin, sidespin, 0.0)

    return ShotTrajectory(
        release_point=release_point,
        velocity=velocity,
        spin=spin,
        release_angle=actual_angle,
        heading_angle=heading,
    )
