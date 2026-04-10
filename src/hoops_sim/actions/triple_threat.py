"""Triple threat mechanics: jab steps, shot fakes, and direct attacks.

When a player catches the ball, they enter triple threat stance and can
jab step, pump fake, or immediately attack. Each option creates different
advantages based on the defender's reaction and player attributes.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.utils.rng import SeededRNG


class TripleThreatAction(enum.Enum):
    """Actions available from triple threat stance."""

    JAB_STEP = "jab_step"
    PUMP_FAKE = "pump_fake"
    DIRECT_DRIVE = "direct_drive"
    DIRECT_SHOOT = "direct_shoot"


@dataclass
class TripleThreatResult:
    """Result of a triple threat action."""

    action: TripleThreatAction
    separation_gained: float = 0.0
    defender_bit: bool = False  # Did the defender react badly?
    foul_drawn: bool = False
    time_cost_ticks: int = 5  # Ticks consumed


def resolve_triple_threat(
    action: TripleThreatAction,
    basketball_iq: int,
    ball_handle: int,
    defender_iq: int,
    defender_consistency: int,
    defender_distance: float,
    rng: SeededRNG,
) -> TripleThreatResult:
    """Resolve a triple threat action.

    Args:
        action: The triple threat action chosen.
        basketball_iq: Offensive player's basketball IQ (0-99).
        ball_handle: Offensive player's ball handling (0-99).
        defender_iq: Defender's basketball IQ (0-99).
        defender_consistency: Defender's defensive consistency (0-99).
        defender_distance: Current distance to defender in feet.
        rng: Random number generator.

    Returns:
        TripleThreatResult with outcome.
    """
    if action == TripleThreatAction.JAB_STEP:
        # Jab step freezes the defender; separation depends on IQ matchup
        fake_quality = basketball_iq / 100.0
        defender_read = defender_consistency / 100.0
        bite_chance = fake_quality * 0.6 - defender_read * 0.3
        bite_chance = max(0.05, min(0.7, bite_chance))

        if rng.random() < bite_chance:
            separation = 0.5 + (1.0 - defender_read) * 1.5
            return TripleThreatResult(
                action=action,
                separation_gained=separation,
                defender_bit=True,
                time_cost_ticks=4,
            )
        return TripleThreatResult(
            action=action,
            separation_gained=0.2,
            time_cost_ticks=4,
        )

    elif action == TripleThreatAction.PUMP_FAKE:
        # Pump fake can draw the defender into the air, creating a drive lane
        # or drawing a foul if the defender makes contact
        fake_quality = basketball_iq / 100.0
        defender_discipline = defender_consistency / 100.0

        bite_chance = fake_quality * 0.5 - defender_discipline * 0.25
        if defender_distance < 3.0:
            bite_chance += 0.15  # Close defender more likely to bite
        bite_chance = max(0.05, min(0.6, bite_chance))

        if rng.random() < bite_chance:
            # Defender bit on the fake
            foul_chance = 0.15 if defender_distance < 2.5 else 0.05
            foul_drawn = rng.random() < foul_chance
            return TripleThreatResult(
                action=action,
                separation_gained=2.0 + rng.uniform(0.0, 1.5),
                defender_bit=True,
                foul_drawn=foul_drawn,
                time_cost_ticks=5,
            )
        return TripleThreatResult(
            action=action,
            separation_gained=0.0,
            time_cost_ticks=5,
        )

    elif action == TripleThreatAction.DIRECT_DRIVE:
        # Immediately put the ball on the floor; quicker but no deception
        quickness_factor = ball_handle / 100.0
        return TripleThreatResult(
            action=action,
            separation_gained=quickness_factor * 1.0,
            time_cost_ticks=3,
        )

    else:  # DIRECT_SHOOT
        return TripleThreatResult(
            action=action,
            separation_gained=0.0,
            time_cost_ticks=2,
        )
