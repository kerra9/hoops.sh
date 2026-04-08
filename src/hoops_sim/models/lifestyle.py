"""Player lifestyle model: off-court factors that affect on-court performance."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerLifestyle:
    """Off-court factors that affect on-court performance.

    These values change over time based on events, team market,
    player personality, and random life events.

    All values range from 0.0 (worst) to 1.0 (best).
    """

    sleep_quality: float = 0.8  # Affected by road trips, time zones, nightlife
    nutrition: float = 0.7  # Affects recovery, energy, weight management
    personal_life: float = 0.8  # Family stability, distractions
    media_pressure: float = 0.3  # Big market = more pressure
    endorsements: float = 0.3  # More endorsements = happier player (morale)
    social_media_presence: float = 0.4  # Can cause drama or boost brand

    def daily_recovery_modifier(self) -> float:
        """Affects between-game energy recovery.

        Returns a multiplier for energy recovery rate.
        Range: ~0.7x to ~1.0x
        """
        base = 1.0
        base *= 0.8 + self.sleep_quality * 0.2  # Sleep: 0.8x to 1.0x
        base *= 0.9 + self.nutrition * 0.1  # Nutrition: 0.9x to 1.0x
        base *= 0.95 + self.personal_life * 0.05  # Distractions: 0.95x to 1.0x
        return base

    def game_day_focus(self) -> float:
        """Affects pre-game energy and mental state.

        Returns a multiplier for game-day performance.
        Range: ~0.90 to 1.0
        """
        if self.media_pressure > 0.8 and self.personal_life < 0.3:
            return 0.90  # Distracted, might not bring full effort
        if self.media_pressure > 0.6 and self.personal_life < 0.5:
            return 0.95
        return 1.0

    def morale_modifier(self) -> float:
        """Overall morale from lifestyle factors.

        Returns a modifier centered around 0.0 (-0.1 to +0.1).
        """
        positive = self.endorsements * 0.03 + self.personal_life * 0.04
        negative = self.media_pressure * 0.03 + (1.0 - self.sleep_quality) * 0.02
        return positive - negative

    def injury_risk_modifier(self) -> float:
        """Lifestyle-based injury risk modifier.

        Poor sleep and nutrition increase injury risk.
        Returns a multiplier (1.0 = normal, >1.0 = higher risk).
        """
        base = 1.0
        if self.sleep_quality < 0.5:
            base += 0.05
        if self.nutrition < 0.5:
            base += 0.05
        return base

    def weight_change_tendency(self) -> float:
        """Tendency to gain or lose weight over the season.

        Returns: negative = losing weight, positive = gaining weight.
        Range: -0.1 to +0.1 lbs per week tendency.
        """
        return (0.5 - self.nutrition) * 0.1
