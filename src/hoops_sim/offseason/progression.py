"""Player progression: between-season development and decline.

Young players improve, prime players hold steady, older players decline.
Work ethic, coaching, and minutes played affect development rate.
"""

from __future__ import annotations

from dataclasses import dataclass, fields

from hoops_sim.models.attributes import PlayerAttributes
from hoops_sim.models.player import Player
from hoops_sim.utils.math import clamp
from hoops_sim.utils.rng import SeededRNG


@dataclass
class ProgressionResult:
    """Result of a player's offseason progression."""

    player_id: int
    player_name: str
    age: int
    old_overall: int
    new_overall: int
    changes: dict[str, int]  # attribute_name -> delta


def progress_player(player: Player, rng: SeededRNG) -> ProgressionResult:
    """Apply offseason development or decline to a player.

    Args:
        player: The player to progress.
        rng: Random number generator.

    Returns:
        ProgressionResult with the changes made.
    """
    old_overall = player.overall
    changes: dict[str, int] = {}

    # Age-based development curve
    age = player.age
    if age <= 22:
        base_change = rng.uniform(1.5, 4.0)  # Big jumps for young players
    elif age <= 25:
        base_change = rng.uniform(0.5, 2.5)  # Still improving
    elif age <= 28:
        base_change = rng.uniform(-0.5, 1.0)  # Peak years, small changes
    elif age <= 31:
        base_change = rng.uniform(-1.5, 0.5)  # Starting to decline
    elif age <= 34:
        base_change = rng.uniform(-3.0, -0.5)  # Declining
    else:
        base_change = rng.uniform(-5.0, -1.5)  # Sharp decline

    # Work ethic modifier (0-99 scale)
    work_ethic = player.attributes.mental.work_ethic
    work_mod = (work_ethic - 50) / 100.0  # -0.5 to +0.5
    base_change += work_mod

    # Apply changes to each attribute category
    attrs = player.attributes
    for cat_field in fields(attrs):
        category = getattr(attrs, cat_field.name)
        for attr_field in fields(category):
            current = getattr(category, attr_field.name)

            # Athletic attributes decline faster with age
            if cat_field.name == "athleticism" and age > 30:
                delta = base_change - rng.uniform(0, 1.5)
            # Mental attributes improve with experience
            elif cat_field.name == "mental" and age > 25:
                delta = base_change + rng.uniform(0, 1.0)
            else:
                delta = base_change + rng.gauss(0, 0.8)

            delta = round(delta)
            new_val = int(clamp(current + delta, 1, 99))
            if new_val != current:
                setattr(category, attr_field.name, new_val)
                full_name = f"{cat_field.name}.{attr_field.name}"
                changes[full_name] = new_val - current

    # Age the player
    player.age += 1

    return ProgressionResult(
        player_id=player.id,
        player_name=player.full_name,
        age=player.age,
        old_overall=old_overall,
        new_overall=player.overall,
        changes=changes,
    )


def progress_roster(roster: list[Player], rng: SeededRNG) -> list[ProgressionResult]:
    """Progress all players on a roster through the offseason."""
    return [progress_player(p, rng) for p in roster]
