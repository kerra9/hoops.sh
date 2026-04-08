"""Deep free throw model with icing, pressure, routine disruption."""

from __future__ import annotations

from hoops_sim.utils.math import clamp
from hoops_sim.utils.rng import SeededRNG


def simulate_free_throw(
    ft_rating: int,
    energy_pct: float,
    composure: int,
    clutch: int,
    is_clutch_time: bool,
    was_timeout_before_ft: bool,
    is_home: bool,
    crowd_energy: float,
    ice_in_veins_tier: int,
    ft_number: int,
    previous_ft_made: bool,
    lane_violation: bool,
    rng: SeededRNG,
) -> bool:
    """Simulate a single free throw attempt.

    Args:
        ft_rating: Free throw attribute (0-99).
        energy_pct: Energy percentage (0-1).
        composure: Composure attribute (0-99).
        clutch: Clutch attribute (0-99).
        is_clutch_time: Whether it's the final 2 minutes of a close game.
        was_timeout_before_ft: Whether opponent called timeout to "ice" the shooter.
        is_home: Whether the shooter is on the home team.
        crowd_energy: Crowd energy level (0-100).
        ice_in_veins_tier: Ice in Veins badge tier (0-4).
        ft_number: Which FT in this trip (1, 2, or 3).
        previous_ft_made: Whether the previous FT in this trip was made.
        lane_violation: Whether a lane violation was called.
        rng: Random number generator.

    Returns:
        True if the free throw is made.
    """
    # Base probability from attribute
    base = ft_rating / 100.0

    # Factor: Fatigue
    fatigue_mod = 0.95 + 0.05 * energy_pct

    # Factor: Clutch pressure
    clutch_mod = 1.0
    if is_clutch_time:
        pressure = 1.0  # Max pressure in clutch
        clutch_mod = 1.0 - pressure * (1 - clutch / 100.0) * 0.10
        # Ice in Veins badge
        if ice_in_veins_tier > 0 and pressure > 0.5:
            clutch_mod += 0.02 * ice_in_veins_tier

    # Factor: Icing (timeout called before FTs)
    ice_mod = 1.0
    if was_timeout_before_ft:
        ice_mod = 0.97
        if composure > 80:
            ice_mod = 0.99

    # Factor: Away crowd hostility
    crowd_mod = 1.0
    if not is_home and crowd_energy > 80:
        crowd_mod = 0.98
        if composure > 85:
            crowd_mod = 0.995

    # Factor: FT streak within trip
    streak_mod = 1.0
    if ft_number > 1:
        streak_mod = 1.01 if previous_ft_made else 0.99

    # Factor: Routine disruption (lane violation)
    routine_mod = 1.0
    if lane_violation:
        routine_mod = 0.98

    final = base * fatigue_mod * clutch_mod * ice_mod * crowd_mod * streak_mod * routine_mod
    final = clamp(final, 0.10, 0.99)

    return rng.random() < final
