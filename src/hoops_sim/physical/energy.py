"""Tick-level energy drain and recovery system."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from hoops_sim.utils.constants import (
    BASE_ENERGY,
    ENERGY_DRAIN_JOG,
    ENERGY_DRAIN_SPRINT,
    ENERGY_DRAIN_STAND,
    ENERGY_DRAIN_WALK,
    ENERGY_RECOVERY_BENCH,
    ENERGY_RECOVERY_HALFTIME,
    ENERGY_RECOVERY_TIMEOUT,
    FATIGUE_THRESHOLD_EXHAUSTED,
    FATIGUE_THRESHOLD_GASSED,
    FATIGUE_THRESHOLD_HEAVY,
    FATIGUE_THRESHOLD_LIGHT,
    FATIGUE_THRESHOLD_MODERATE,
)
from hoops_sim.utils.math import clamp


@dataclass
class EnergyState:
    """Tracks a player's energy level during a game."""

    current: float = BASE_ENERGY
    max_energy: float = BASE_ENERGY

    @property
    def pct(self) -> float:
        if self.max_energy <= 0:
            return 0.0
        return self.current / self.max_energy

    def drain(self, amount: float) -> None:
        self.current = max(0.0, self.current - amount)

    def recover(self, amount: float) -> None:
        self.current = min(self.max_energy, self.current + amount)

    def fatigue_tier(self) -> int:
        """Get fatigue tier (0=fresh, 1-5=increasingly fatigued)."""
        pct = self.pct
        if pct >= FATIGUE_THRESHOLD_LIGHT:
            return 0
        if pct >= FATIGUE_THRESHOLD_MODERATE:
            return 1
        if pct >= FATIGUE_THRESHOLD_HEAVY:
            return 2
        if pct >= FATIGUE_THRESHOLD_EXHAUSTED:
            return 3
        if pct >= FATIGUE_THRESHOLD_GASSED:
            return 4
        return 5

    def fatigue_penalty(self) -> float:
        """Performance penalty from fatigue. 1.0=no penalty, lower=worse."""
        tier = self.fatigue_tier()
        return {0: 1.0, 1: 0.97, 2: 0.93, 3: 0.87, 4: 0.78, 5: 0.65}[tier]


class EnergyManager:
    """Manages energy for all players in a game."""

    def __init__(self) -> None:
        self.states: Dict[int, EnergyState] = {}

    def init_player(self, player_id: int, stamina: int) -> None:
        """Initialize energy for a player based on stamina attribute."""
        max_e = BASE_ENERGY + stamina / 100.0 * 20.0
        self.states[player_id] = EnergyState(current=max_e, max_energy=max_e)

    def get(self, player_id: int) -> EnergyState:
        return self.states.get(player_id, EnergyState())

    def drain_action(self, player_id: int, action_cost: float, surface_modifier: float = 1.0) -> None:
        """Drain energy for an action."""
        state = self.states.get(player_id)
        if state:
            state.drain(action_cost * surface_modifier)

    def recover_bench(self, player_id: int, ticks: int = 1) -> None:
        """Recover energy while on the bench."""
        state = self.states.get(player_id)
        if state:
            state.recover(ENERGY_RECOVERY_BENCH * ticks)

    def recover_timeout(self, player_ids: list) -> None:
        """Recover energy during a timeout for players on court."""
        for pid in player_ids:
            state = self.states.get(pid)
            if state:
                state.recover(ENERGY_RECOVERY_TIMEOUT)

    def recover_halftime(self, player_ids: list) -> None:
        """Recover energy during halftime."""
        for pid in player_ids:
            state = self.states.get(pid)
            if state:
                state.recover(ENERGY_RECOVERY_HALFTIME)
