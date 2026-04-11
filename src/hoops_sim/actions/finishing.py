"""Finishing move selection and resolution for at-rim attempts.

When a player drives to the basket, they select a finishing move based
on their attributes, the defensive presence, and the situation.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.utils.rng import SeededRNG


class FinishType(enum.Enum):
    """Types of finishing moves at the rim."""

    LAYUP = "layup"
    DRIVING_DUNK = "driving_dunk"
    STANDING_DUNK = "standing_dunk"
    FLOATER = "floater"
    EURO_STEP = "euro_step"
    REVERSE_LAYUP = "reverse_layup"
    FINGER_ROLL = "finger_roll"
    HOOK_SHOT = "hook_shot"
    PUTBACK_DUNK = "putback_dunk"


@dataclass
class FinishSpec:
    """Specification for a finishing move."""

    primary_attribute: str  # Which attribute drives success
    release_time_ticks: int  # How long the finish takes
    blockability: float  # 0-1, how easy it is to block
    contact_tolerance: float  # How well the finish handles contact
    foul_draw_bonus: float  # Bonus to foul drawing probability


FINISH_SPECS: dict[FinishType, FinishSpec] = {
    FinishType.LAYUP: FinishSpec(
        primary_attribute="layup", release_time_ticks=4,
        blockability=0.6, contact_tolerance=0.4, foul_draw_bonus=0.0,
    ),
    FinishType.DRIVING_DUNK: FinishSpec(
        primary_attribute="driving_dunk", release_time_ticks=5,
        blockability=0.4, contact_tolerance=0.7, foul_draw_bonus=0.05,
    ),
    FinishType.STANDING_DUNK: FinishSpec(
        primary_attribute="standing_dunk", release_time_ticks=4,
        blockability=0.3, contact_tolerance=0.8, foul_draw_bonus=0.03,
    ),
    FinishType.FLOATER: FinishSpec(
        primary_attribute="acrobatic_finish", release_time_ticks=3,
        blockability=0.2, contact_tolerance=0.3, foul_draw_bonus=-0.02,
    ),
    FinishType.EURO_STEP: FinishSpec(
        primary_attribute="acrobatic_finish", release_time_ticks=5,
        blockability=0.25, contact_tolerance=0.5, foul_draw_bonus=0.03,
    ),
    FinishType.REVERSE_LAYUP: FinishSpec(
        primary_attribute="acrobatic_finish", release_time_ticks=5,
        blockability=0.2, contact_tolerance=0.4, foul_draw_bonus=0.01,
    ),
    FinishType.FINGER_ROLL: FinishSpec(
        primary_attribute="acrobatic_finish", release_time_ticks=3,
        blockability=0.35, contact_tolerance=0.3, foul_draw_bonus=0.0,
    ),
    FinishType.HOOK_SHOT: FinishSpec(
        primary_attribute="post_hook", release_time_ticks=5,
        blockability=0.2, contact_tolerance=0.5, foul_draw_bonus=0.02,
    ),
    FinishType.PUTBACK_DUNK: FinishSpec(
        primary_attribute="standing_dunk", release_time_ticks=3,
        blockability=0.3, contact_tolerance=0.8, foul_draw_bonus=0.04,
    ),
}


@dataclass
class FinishResult:
    """Result of selecting and attempting a finish."""

    finish_type: FinishType
    success_modifier: float = 0.0  # Modifier to base shot probability
    block_vulnerability: float = 0.5  # How vulnerable to blocks
    foul_draw_chance: float = 0.1  # Chance of drawing a foul
    is_dunk: bool = False
    is_poster: bool = False  # Dunked on a defender


def select_finish_type(
    layup: int,
    driving_dunk: int,
    standing_dunk: int,
    acrobatic_finish: int,
    post_hook: int,
    vertical_leap: int,
    speed: int,
    defender_distance: float,
    rim_protector_present: bool,
    has_contact_finisher: bool,
    has_slithery_finisher: bool,
    has_posterizer: bool,
    has_acrobat: bool,
    is_putback: bool,
    rng: SeededRNG,
) -> FinishResult:
    """Select the best finishing move for the situation.

    Args:
        layup: Player's layup rating.
        driving_dunk: Player's driving dunk rating.
        standing_dunk: Player's standing dunk rating.
        acrobatic_finish: Player's acrobatic finish rating.
        post_hook: Player's post hook rating.
        vertical_leap: Player's vertical leap.
        speed: Player's speed rating.
        defender_distance: Distance to nearest defender.
        rim_protector_present: Whether a rim protector is nearby.
        has_contact_finisher: Whether player has contact finisher badge.
        has_slithery_finisher: Whether player has slithery finisher badge.
        has_posterizer: Whether player has posterizer badge.
        has_acrobat: Whether player has acrobat badge.
        is_putback: Whether this is an offensive rebound putback.
        rng: Random number generator.

    Returns:
        FinishResult with the selected finish and modifiers.
    """
    if is_putback and standing_dunk > 65 and vertical_leap > 70:
        return FinishResult(
            finish_type=FinishType.PUTBACK_DUNK,
            success_modifier=0.05,
            block_vulnerability=0.3,
            foul_draw_chance=0.12,
            is_dunk=True,
        )

    candidates: list[tuple[FinishType, float]] = []

    # Layup is always available
    layup_score = layup / 99.0
    candidates.append((FinishType.LAYUP, layup_score))

    # Driving dunk requires threshold + clear-ish path
    if driving_dunk > 55 and vertical_leap > 50:
        dunk_score = driving_dunk / 99.0
        if defender_distance < 2.0 and not has_posterizer:
            dunk_score *= 0.5  # Contested dunk harder without posterizer
        elif defender_distance < 2.0 and has_posterizer:
            dunk_score *= 0.8  # Posterizer helps
        candidates.append((FinishType.DRIVING_DUNK, dunk_score))

    # Floater when rim protector is present
    if acrobatic_finish > 50 and rim_protector_present:
        floater_score = acrobatic_finish / 99.0 * 1.1  # Bonus in this situation
        if has_acrobat:
            floater_score *= 1.15
        candidates.append((FinishType.FLOATER, floater_score))

    # Euro-step to avoid contact
    if acrobatic_finish > 55 and speed > 60:
        euro_score = acrobatic_finish / 99.0
        if has_slithery_finisher:
            euro_score *= 1.15
        if defender_distance < 3.0:
            euro_score *= 1.1  # Euro-step shines when contested
        candidates.append((FinishType.EURO_STEP, euro_score))

    # Reverse layup to use rim as protection
    if acrobatic_finish > 50:
        reverse_score = acrobatic_finish / 99.0 * 0.9
        if rim_protector_present:
            reverse_score *= 1.2  # Good counter to rim protectors
        candidates.append((FinishType.REVERSE_LAYUP, reverse_score))

    # Finger roll for soft touch
    if acrobatic_finish > 60:
        finger_score = acrobatic_finish / 99.0 * 0.85
        candidates.append((FinishType.FINGER_ROLL, finger_score))

    # Note: candidates always has at least the LAYUP entry from above.
    # Add noise and pick the best
    scored = [(ft, score + rng.gauss(0, 0.08)) for ft, score in candidates]
    best_type, best_score = max(scored, key=lambda x: x[1])

    spec = FINISH_SPECS[best_type]
    is_dunk = best_type in (FinishType.DRIVING_DUNK, FinishType.STANDING_DUNK,
                            FinishType.PUTBACK_DUNK)

    # Check for poster dunk
    is_poster = False
    if is_dunk and defender_distance < 2.0 and has_posterizer:
        is_poster = rng.random() < 0.25

    # Calculate modifiers
    success_mod = 0.0
    if has_contact_finisher and defender_distance < 2.0:
        success_mod += 0.05
    if has_slithery_finisher and best_type == FinishType.EURO_STEP:
        success_mod += 0.04
    if has_acrobat and best_type in (FinishType.FLOATER, FinishType.FINGER_ROLL):
        success_mod += 0.04

    foul_chance = 0.10 + spec.foul_draw_bonus
    if has_contact_finisher:
        foul_chance += 0.03
    if defender_distance < 2.0:
        foul_chance += 0.05

    return FinishResult(
        finish_type=best_type,
        success_modifier=success_mod,
        block_vulnerability=spec.blockability,
        foul_draw_chance=foul_chance,
        is_dunk=is_dunk,
        is_poster=is_poster,
    )
