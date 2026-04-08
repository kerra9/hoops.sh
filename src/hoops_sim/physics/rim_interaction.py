"""Rim interaction: collision detection, carom direction, rattle-in physics."""

from __future__ import annotations

import enum
import math
from dataclasses import dataclass
from typing import Optional

from hoops_sim.physics.shot_trajectory import ShotTrajectory
from hoops_sim.physics.vec import Vec2, Vec3
from hoops_sim.utils.constants import (
    BACKSPIN_COR_BONUS,
    BASKET_HEIGHT,
    BASKET_X,
    BASKET_Y,
    BALL_RADIUS,
    CAROM_BACKSPIN_DAMPEN_FACTOR,
    CAROM_DISTANCE_BASE,
    CAROM_NOISE_DEGREES,
    CAROM_NOISE_DISTANCE,
    CAROM_SPIN_LATERAL_FACTOR,
    RIM_COEFFICIENT_OF_RESTITUTION,
    RIM_HARD_HIT_THRESHOLD,
    RIM_MISS_THRESHOLD,
    RIM_GRAZE_THRESHOLD,
    RIM_RADIUS,
    SWISH_THRESHOLD,
)
from hoops_sim.utils.rng import SeededRNG


BASKET_CENTER = Vec3(BASKET_X, BASKET_Y, BASKET_HEIGHT)
BASKET_CENTER_2D = Vec2(BASKET_X, BASKET_Y)


class ShotOutcome(enum.Enum):
    """Possible outcomes when a shot reaches the basket."""

    SWISH = "swish"
    RATTLE_IN = "rattle_in"
    RIM_OUT = "rim_out"
    BACKBOARD = "backboard"
    AIRBALL = "airball"


@dataclass
class CaromResult:
    """Direction and distance of a rebound carom off the rim."""

    angle: float  # degrees: direction the ball bounces (0 = positive x)
    distance_ft: float  # how far from the rim the ball lands


@dataclass
class RimInteractionResult:
    """Full result of a shot interacting with the rim."""

    outcome: ShotOutcome
    made: bool
    carom: Optional[CaromResult] = None  # Only for misses


def calculate_entry_offset(
    ball_position: Vec3,
    ball_velocity: Vec3,
) -> float:
    """Calculate how far from the center of the rim the ball enters.

    This measures the horizontal offset in inches between the ball's center
    and the rim's center at the plane of the rim.

    Returns:
        Offset in inches from the center of the rim.
    """
    # Project where the ball crosses the rim height plane
    # We look at the XY distance from the basket center
    dx = ball_position.x - BASKET_CENTER.x
    dy = ball_position.y - BASKET_CENTER.y
    offset_ft = math.hypot(dx, dy)
    return offset_ft * 12.0  # Convert to inches


def calculate_rim_contact_angle(entry_offset_inches: float, speed: float) -> float:
    """Calculate the angle of contact with the rim.

    Higher entry offset and speed mean harder contact.

    Returns:
        Contact angle factor (0 to ~90), where higher = harder contact.
    """
    # Normalize: entry offset contributes most, speed adds intensity
    return entry_offset_inches * 8.0 + speed * 0.5


def calculate_carom_direction(
    ball_position: Vec3,
    contact_angle: float,
    spin: Vec3,
    rng: SeededRNG,
) -> CaromResult:
    """Determine where the rebound goes after a rim miss.

    Rules:
    - Shots from the left tend to carom right (and vice versa)
    - Long shots produce long rebounds
    - Short shots produce short rebounds
    - Backspin reduces carom distance
    - Sidespin shifts the carom laterally

    Args:
        ball_position: Ball position at rim contact.
        contact_angle: How hard the ball hit the rim.
        spin: Ball spin vector (backspin in x, sidespin in y).
        rng: Random number generator.

    Returns:
        CaromResult with angle and distance.
    """
    # Base direction: opposite of where the shot came from
    dx = ball_position.x - BASKET_CENTER.x
    dy = ball_position.y - BASKET_CENTER.y
    incoming_angle = math.degrees(math.atan2(dy, dx))
    base_direction = (incoming_angle + 180.0) % 360.0  # Opposite direction

    # Spin adjustments
    spin_lateral = spin.y * CAROM_SPIN_LATERAL_FACTOR  # Sidespin shifts angle
    backspin_dampen = 1.0 - spin.x / CAROM_BACKSPIN_DAMPEN_FACTOR  # Backspin reduces distance
    backspin_dampen = max(0.3, min(1.0, backspin_dampen))

    # Add randomness
    carom_angle = base_direction + spin_lateral + rng.gauss(0, CAROM_NOISE_DEGREES)
    carom_distance = (
        contact_angle * CAROM_DISTANCE_BASE * backspin_dampen
        + rng.gauss(0, CAROM_NOISE_DISTANCE)
    )
    carom_distance = max(0.5, carom_distance)  # Minimum distance

    return CaromResult(angle=carom_angle % 360.0, distance_ft=carom_distance)


def resolve_backboard_interaction(
    ball_velocity: Vec3,
    spin: Vec3,
    rng: SeededRNG,
) -> RimInteractionResult:
    """Handle a shot that hits the backboard.

    A high-arc shot hitting the backboard may still bank in.

    Returns:
        RimInteractionResult indicating whether the bank shot went in.
    """
    # Bank shot probability: depends on angle and spin
    speed = ball_velocity.magnitude()
    # Softer shots off the backboard are more likely to go in
    bank_probability = max(0.0, 0.35 - speed * 0.01)
    # Good backspin helps
    if spin.x > 100:
        bank_probability += 0.10

    if rng.random() < bank_probability:
        return RimInteractionResult(outcome=ShotOutcome.RATTLE_IN, made=True)

    # Miss off backboard
    carom = CaromResult(
        angle=rng.uniform(0, 360),
        distance_ft=rng.uniform(1.0, 4.0),
    )
    return RimInteractionResult(outcome=ShotOutcome.BACKBOARD, made=False, carom=carom)


def resolve_rim_interaction(
    ball_position: Vec3,
    ball_velocity: Vec3,
    spin: Vec3,
    rng: SeededRNG,
) -> RimInteractionResult:
    """Resolve what happens when a shot reaches the basket area.

    Models the physical interaction between the ball and rim, determining
    whether the shot is a swish, rattle-in, rim-out, backboard hit, or airball.

    Args:
        ball_position: Ball position when it reaches the rim plane.
        ball_velocity: Ball velocity at the rim plane.
        spin: Ball spin vector.
        rng: Random number generator.

    Returns:
        RimInteractionResult with the outcome and optional carom info.
    """
    entry_offset = calculate_entry_offset(ball_position, ball_velocity)

    # Zone 1: Perfect center -- SWISH
    if entry_offset < SWISH_THRESHOLD:
        return RimInteractionResult(outcome=ShotOutcome.SWISH, made=True)

    # Zone 2: Ball fits through but may graze the rim
    if entry_offset < RIM_GRAZE_THRESHOLD:
        contact_angle = calculate_rim_contact_angle(entry_offset, ball_velocity.magnitude())

        # Backspin helps: ball with good backspin "dies" on the rim
        spin_factor = spin.x / 200.0  # Normalize backspin (0 to ~1.0)
        spin_factor = max(0.0, min(1.0, spin_factor))
        bounce_energy = contact_angle * (
            1.0 - RIM_COEFFICIENT_OF_RESTITUTION * (1.0 + spin_factor * BACKSPIN_COR_BONUS)
        )

        # Lower bounce energy = more likely to go in
        make_threshold = 25.0 + spin_factor * 10.0  # Higher spin = more forgiving
        if bounce_energy < make_threshold:
            return RimInteractionResult(outcome=ShotOutcome.RATTLE_IN, made=True)

        # Rim out
        carom = calculate_carom_direction(ball_position, contact_angle, spin, rng)
        return RimInteractionResult(outcome=ShotOutcome.RIM_OUT, made=False, carom=carom)

    # Zone 3: Hard rim hit
    if entry_offset < RIM_HARD_HIT_THRESHOLD:
        # High-arc shots might bank in off the backboard
        if ball_velocity.z < -5.0:  # Steep downward angle
            return resolve_backboard_interaction(ball_velocity, spin, rng)

        contact_angle = calculate_rim_contact_angle(entry_offset, ball_velocity.magnitude())
        carom = calculate_carom_direction(ball_position, contact_angle, spin, rng)
        return RimInteractionResult(outcome=ShotOutcome.RIM_OUT, made=False, carom=carom)

    # Zone 4: Hits backboard only
    if entry_offset < RIM_MISS_THRESHOLD:
        return resolve_backboard_interaction(ball_velocity, spin, rng)

    # Zone 5: Complete airball
    return RimInteractionResult(
        outcome=ShotOutcome.AIRBALL,
        made=False,
        carom=CaromResult(
            angle=rng.uniform(0, 360),
            distance_ft=rng.uniform(3.0, 8.0),
        ),
    )
