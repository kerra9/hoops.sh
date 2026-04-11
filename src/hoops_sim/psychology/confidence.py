"""Per-player confidence tracker."""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.utils.math import clamp


@dataclass
class ConfidenceTracker:
    """Tracks per-player confidence levels during a game.

    Confidence rises on made shots and positive plays, falls on misses.
    Affects shot selection and shooting probability.
    """

    player_confidence: dict[int, float] = field(default_factory=dict)

    def get(self, player_id: int) -> float:
        """Get a player's confidence. Default is 0.0 (neutral)."""
        return self.player_confidence.get(player_id, 0.0)

    def on_made_shot(self, player_id: int, was_three: bool = False,
                     volatility: float = 1.0) -> None:
        """Record a made shot. volatility scales the confidence swing (Phase 2: Personality)."""
        current = self.get(player_id)
        boost = (0.08 if was_three else 0.05) * volatility
        self.player_confidence[player_id] = clamp(current + boost, -0.3, 0.3)

    def on_missed_shot(self, player_id: int, volatility: float = 1.0) -> None:
        """Record a missed shot. volatility scales the confidence swing (Phase 2: Personality)."""
        current = self.get(player_id)
        penalty = 0.03 * volatility
        self.player_confidence[player_id] = clamp(current - penalty, -0.3, 0.3)

    def on_assist(self, player_id: int) -> None:
        current = self.get(player_id)
        self.player_confidence[player_id] = clamp(current + 0.03, -0.3, 0.3)

    def on_turnover(self, player_id: int) -> None:
        current = self.get(player_id)
        self.player_confidence[player_id] = clamp(current - 0.05, -0.3, 0.3)

    def on_block(self, player_id: int) -> None:
        """Player got blocked."""
        current = self.get(player_id)
        self.player_confidence[player_id] = clamp(current - 0.04, -0.3, 0.3)

    def on_and_one(self, player_id: int) -> None:
        current = self.get(player_id)
        self.player_confidence[player_id] = clamp(current + 0.10, -0.3, 0.3)

    def shooting_modifier(self, player_id: int) -> float:
        """Get shooting probability modifier from confidence. Range ~0.97 to 1.03."""
        return 1.0 + self.get(player_id) * 0.1

    def decay_all(self) -> None:
        """Natural decay toward neutral each possession."""
        for pid in self.player_confidence:
            self.player_confidence[pid] *= 0.97
