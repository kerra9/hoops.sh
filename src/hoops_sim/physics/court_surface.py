"""Court surface model: grip, altitude, and environmental conditions."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Optional

from hoops_sim.utils.constants import (
    ALTITUDE_BALL_BOUNCE_FACTOR_PER_1000FT,
    ALTITUDE_STAMINA_DRAIN_PER_1000FT,
    DEFAULT_GRIP_COEFFICIENT,
    HUMIDITY_GRIP_PENALTY,
    HUMIDITY_GRIP_THRESHOLD,
    WORN_SURFACE_GRIP_PENALTY,
)


class SurfaceCondition(enum.Enum):
    """Condition of the court surface."""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    WORN = "worn"


@dataclass
class ShoeGrip:
    """Shoe grip properties."""

    grip: float = 0.95  # 0-1: shoe traction coefficient


@dataclass
class CourtSurface:
    """Physical properties of the court surface and arena environment.

    Models how the court surface, altitude, temperature, and humidity affect
    gameplay. These factors influence traction, stamina drain, ball bounce,
    and injury risk.
    """

    material: str = "maple"
    condition: SurfaceCondition = SurfaceCondition.GOOD
    grip_coefficient: float = DEFAULT_GRIP_COEFFICIENT
    altitude_ft: int = 0
    temperature_f: int = 68
    humidity_pct: int = 45

    def get_traction(self, shoes: Optional[ShoeGrip] = None) -> float:
        """Calculate effective traction for a player.

        Traction affects:
        - Cut sharpness (high traction = sharper cuts)
        - Stop speed (high traction = faster stops)
        - Slip probability (low traction = occasional slips, injury risk)
        - Driving explosiveness (first step relies on traction)

        Args:
            shoes: Player's shoe grip properties. Defaults to standard grip.

        Returns:
            Effective traction coefficient (0-1).
        """
        shoe_grip = shoes.grip if shoes else 0.95
        base = self.grip_coefficient * shoe_grip

        # Worn surface reduces grip
        if self.condition == SurfaceCondition.WORN:
            base -= WORN_SURFACE_GRIP_PENALTY

        # High humidity (sweat on floor) reduces grip
        if self.humidity_pct > HUMIDITY_GRIP_THRESHOLD:
            base -= HUMIDITY_GRIP_PENALTY

        # Fair condition is slightly worse than good
        if self.condition == SurfaceCondition.FAIR:
            base -= WORN_SURFACE_GRIP_PENALTY * 0.5

        return max(0.5, min(1.0, base))

    def get_stamina_drain_modifier(self) -> float:
        """Get the stamina drain multiplier from altitude.

        Denver's altitude (5,280 ft) means visiting players drain stamina
        ~3% faster. This reflects lower oxygen levels at altitude.

        Returns:
            Multiplier for stamina drain (1.0 = no effect, >1.0 = drains faster).
        """
        altitude_thousands = self.altitude_ft / 1000.0
        return 1.0 + altitude_thousands * ALTITUDE_STAMINA_DRAIN_PER_1000FT

    def get_ball_bounce_modifier(self) -> float:
        """Get the ball bounce modifier from altitude.

        Less air resistance at altitude means the ball bounces slightly
        differently (higher, slightly less drag).

        Returns:
            Multiplier for ball bounce (1.0 = no effect).
        """
        altitude_thousands = self.altitude_ft / 1000.0
        return 1.0 + altitude_thousands * ALTITUDE_BALL_BOUNCE_FACTOR_PER_1000FT

    def get_slip_probability(self, shoes: Optional[ShoeGrip] = None) -> float:
        """Calculate the probability of a player slipping per high-intensity action.

        Low traction increases slip probability. Slips can lead to turnovers
        and injuries.

        Returns:
            Probability of slipping (0 to ~0.05).
        """
        traction = self.get_traction(shoes)
        # Base slip chance is very low with good traction
        if traction > 0.90:
            return 0.001
        if traction > 0.80:
            return 0.005
        if traction > 0.70:
            return 0.015
        return 0.03


# Pre-configured arena surfaces for notable venues
DENVER_SURFACE = CourtSurface(
    material="maple",
    condition=SurfaceCondition.EXCELLENT,
    grip_coefficient=0.96,
    altitude_ft=5280,
    temperature_f=68,
    humidity_pct=30,
)

MIAMI_SURFACE = CourtSurface(
    material="maple",
    condition=SurfaceCondition.GOOD,
    grip_coefficient=0.94,
    altitude_ft=6,
    temperature_f=72,
    humidity_pct=65,
)

DEFAULT_SURFACE = CourtSurface()
