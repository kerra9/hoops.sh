"""Tests for injury risk system."""

from __future__ import annotations

import pytest

from hoops_sim.injury.risk import (
    INJURY_RECOVERY,
    Injury,
    InjurySeverity,
    InjuryType,
    calculate_injury_risk,
)
from hoops_sim.utils.rng import SeededRNG


class TestInjury:
    def test_recovery(self):
        inj = Injury(
            injury_type=InjuryType.ANKLE_SPRAIN,
            severity=InjurySeverity.MINOR,
            games_remaining=3,
            games_total=3,
        )
        assert not inj.is_healed
        inj.recover_game()
        assert inj.games_remaining == 2
        inj.recover_game()
        inj.recover_game()
        assert inj.is_healed

    def test_recovery_pct(self):
        inj = Injury(
            injury_type=InjuryType.HAMSTRING_STRAIN,
            severity=InjurySeverity.MODERATE,
            games_remaining=10,
            games_total=10,
        )
        assert inj.recovery_pct == pytest.approx(0.0)
        inj.recover_game()
        assert inj.recovery_pct == pytest.approx(0.1)

    def test_all_injuries_have_recovery(self):
        for inj_type in InjuryType:
            assert inj_type in INJURY_RECOVERY
            lo, hi = INJURY_RECOVERY[inj_type]
            assert lo > 0
            assert hi >= lo


class TestCalculateInjuryRisk:
    def test_mostly_no_injury(self):
        """Most actions should not cause injury."""
        injuries = 0
        for seed in range(1000):
            result = calculate_injury_risk(
                durability=80, age=25, energy_pct=1.0,
                is_contact=False, contact_severity=0.0,
                medical_prevention_mod=0.9, rng=SeededRNG(seed),
            )
            if result is not None:
                injuries += 1
        assert injuries < 5  # Very rare

    def test_contact_increases_risk(self):
        no_contact = sum(
            1 for seed in range(5000)
            if calculate_injury_risk(
                durability=50, age=30, energy_pct=0.5,
                is_contact=False, contact_severity=0.0,
                medical_prevention_mod=1.0, rng=SeededRNG(seed),
            ) is not None
        )
        with_contact = sum(
            1 for seed in range(5000)
            if calculate_injury_risk(
                durability=50, age=30, energy_pct=0.5,
                is_contact=True, contact_severity=0.7,
                medical_prevention_mod=1.0, rng=SeededRNG(seed),
            ) is not None
        )
        assert with_contact >= no_contact

    def test_injury_has_valid_recovery(self):
        for seed in range(10000):
            result = calculate_injury_risk(
                durability=30, age=35, energy_pct=0.2,
                is_contact=True, contact_severity=0.8,
                medical_prevention_mod=1.0, rng=SeededRNG(seed),
            )
            if result is not None:
                assert result.games_remaining > 0
                assert result.games_total > 0
                break
