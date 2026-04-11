"""Injury risk calculation and injury types."""

from __future__ import annotations

import enum
from dataclasses import dataclass

from hoops_sim.utils.rng import SeededRNG


class InjuryType(enum.Enum):
    """Types of injuries."""

    # Minor (1-3 games)
    ANKLE_SPRAIN = "ankle_sprain"
    KNEE_CONTUSION = "knee_contusion"
    HIP_CONTUSION = "hip_contusion"
    FINGER_SPRAIN = "finger_sprain"
    WRIST_SPRAIN = "wrist_sprain"
    BACK_SPASMS = "back_spasms"
    CALF_STRAIN = "calf_strain"

    # Moderate (4-15 games)
    HAMSTRING_STRAIN = "hamstring_strain"
    GROIN_STRAIN = "groin_strain"
    QUAD_STRAIN = "quad_strain"
    SHOULDER_SPRAIN = "shoulder_sprain"
    CONCUSSION = "concussion"
    RIB_CONTUSION = "rib_contusion"
    FOOT_SPRAIN = "foot_sprain"

    # Serious (16-40 games)
    MCL_SPRAIN = "mcl_sprain"
    HIGH_ANKLE_SPRAIN = "high_ankle_sprain"
    BROKEN_HAND = "broken_hand"
    BROKEN_NOSE = "broken_nose"
    PLANTAR_FASCIITIS = "plantar_fasciitis"

    # Severe (40+ games / season-ending)
    ACL_TEAR = "acl_tear"
    ACHILLES_TEAR = "achilles_tear"
    MENISCUS_TEAR = "meniscus_tear"
    BROKEN_LEG = "broken_leg"
    BROKEN_FOOT = "broken_foot"


class InjurySeverity(enum.Enum):
    MINOR = "minor"  # 1-3 games
    MODERATE = "moderate"  # 4-15 games
    SERIOUS = "serious"  # 16-40 games
    SEVERE = "severe"  # 40+ games


# Recovery time ranges in games
INJURY_RECOVERY: dict[InjuryType, tuple[int, int]] = {
    InjuryType.ANKLE_SPRAIN: (1, 4),
    InjuryType.KNEE_CONTUSION: (1, 3),
    InjuryType.HIP_CONTUSION: (1, 3),
    InjuryType.FINGER_SPRAIN: (1, 5),
    InjuryType.WRIST_SPRAIN: (2, 5),
    InjuryType.BACK_SPASMS: (1, 5),
    InjuryType.CALF_STRAIN: (2, 6),
    InjuryType.HAMSTRING_STRAIN: (5, 15),
    InjuryType.GROIN_STRAIN: (5, 15),
    InjuryType.QUAD_STRAIN: (4, 12),
    InjuryType.SHOULDER_SPRAIN: (5, 12),
    InjuryType.CONCUSSION: (3, 14),
    InjuryType.RIB_CONTUSION: (3, 10),
    InjuryType.FOOT_SPRAIN: (5, 14),
    InjuryType.MCL_SPRAIN: (15, 35),
    InjuryType.HIGH_ANKLE_SPRAIN: (15, 30),
    InjuryType.BROKEN_HAND: (15, 30),
    InjuryType.BROKEN_NOSE: (1, 5),
    InjuryType.PLANTAR_FASCIITIS: (10, 40),
    InjuryType.ACL_TEAR: (50, 82),
    InjuryType.ACHILLES_TEAR: (50, 82),
    InjuryType.MENISCUS_TEAR: (20, 50),
    InjuryType.BROKEN_LEG: (40, 82),
    InjuryType.BROKEN_FOOT: (30, 60),
}


@dataclass
class Injury:
    """An active injury on a player."""

    injury_type: InjuryType
    severity: InjurySeverity
    games_remaining: int
    games_total: int
    occurred_in_game: bool = True  # vs practice/off-court

    def recover_game(self) -> bool:
        """Advance recovery by one game. Returns True if healed."""
        self.games_remaining = max(0, self.games_remaining - 1)
        return self.games_remaining == 0

    @property
    def is_healed(self) -> bool:
        return self.games_remaining <= 0

    @property
    def recovery_pct(self) -> float:
        if self.games_total <= 0:
            return 1.0
        return 1.0 - (self.games_remaining / self.games_total)


def calculate_injury_risk(
    durability: int,
    age: int,
    energy_pct: float,
    is_contact: bool,
    contact_severity: float,
    medical_prevention_mod: float,
    rng: SeededRNG,
) -> Injury | None:
    """Calculate whether an injury occurs on this action.

    Args:
        durability: Player's durability attribute (0-99).
        age: Player's age.
        energy_pct: Current energy percentage (0-1).
        is_contact: Whether this was a contact play.
        contact_severity: Severity of contact if applicable (0-1).
        medical_prevention_mod: Medical staff modifier (0.85-1.0, lower=better).
        rng: Random number generator.

    Returns:
        An Injury if one occurs, None otherwise.
    """
    # Base risk per action is very low
    base_risk = 0.0001  # 0.01% per action

    # Durability reduces risk
    durability_mod = 1.5 - durability / 100.0  # 0.5 to 1.5

    # Age increases risk after 30
    age_mod = 1.0
    if age > 32:
        age_mod = 1.0 + (age - 32) * 0.1
    elif age > 28:
        age_mod = 1.0 + (age - 28) * 0.03

    # Fatigue increases risk
    fatigue_mod = 1.0
    if energy_pct < 0.3:
        fatigue_mod = 1.5
    elif energy_pct < 0.5:
        fatigue_mod = 1.2

    # Contact increases risk
    contact_mod = 1.0 + contact_severity * 3.0 if is_contact else 1.0

    # Medical staff prevention
    total_risk = (
        base_risk * durability_mod * age_mod * fatigue_mod
        * contact_mod * medical_prevention_mod
    )

    if rng.random() > total_risk:
        return None

    # Injury occurred -- determine type and severity
    severity_roll = rng.random()
    if severity_roll < 0.55:
        # Minor injury
        minor_types = [
            InjuryType.ANKLE_SPRAIN, InjuryType.KNEE_CONTUSION,
            InjuryType.FINGER_SPRAIN, InjuryType.BACK_SPASMS,
            InjuryType.CALF_STRAIN,
        ]
        inj_type = rng.choice(minor_types)
        severity = InjurySeverity.MINOR
    elif severity_roll < 0.85:
        # Moderate injury
        mod_types = [
            InjuryType.HAMSTRING_STRAIN, InjuryType.GROIN_STRAIN,
            InjuryType.CONCUSSION, InjuryType.FOOT_SPRAIN,
        ]
        inj_type = rng.choice(mod_types)
        severity = InjurySeverity.MODERATE
    elif severity_roll < 0.96:
        # Serious
        serious_types = [
            InjuryType.MCL_SPRAIN, InjuryType.HIGH_ANKLE_SPRAIN,
            InjuryType.BROKEN_HAND,
        ]
        inj_type = rng.choice(serious_types)
        severity = InjurySeverity.SERIOUS
    else:
        # Severe
        severe_types = [
            InjuryType.ACL_TEAR, InjuryType.ACHILLES_TEAR,
            InjuryType.MENISCUS_TEAR,
        ]
        inj_type = rng.choice(severe_types)
        severity = InjurySeverity.SEVERE

    lo, hi = INJURY_RECOVERY[inj_type]
    games = rng.randint(lo, hi)

    return Injury(
        injury_type=inj_type,
        severity=severity,
        games_remaining=games,
        games_total=games,
    )
