"""Tests for finishing move selection and resolution."""

from __future__ import annotations

import pytest

from hoops_sim.actions.finishing import (
    FINISH_SPECS,
    FinishResult,
    FinishType,
    select_finish_type,
)
from hoops_sim.utils.rng import SeededRNG


@pytest.fixture
def rng():
    return SeededRNG(seed=42)


class TestFinishTypeSelection:
    def test_returns_finish_result(self, rng):
        result = select_finish_type(
            layup=75, driving_dunk=60, standing_dunk=55,
            acrobatic_finish=65, post_hook=40, vertical_leap=70,
            speed=75, defender_distance=3.0,
            rim_protector_present=False,
            has_contact_finisher=False, has_slithery_finisher=False,
            has_posterizer=False, has_acrobat=False,
            is_putback=False, rng=rng,
        )
        assert isinstance(result, FinishResult)
        assert isinstance(result.finish_type, FinishType)
        assert 0.0 <= result.block_vulnerability <= 1.0
        assert result.foul_draw_chance > 0

    def test_putback_dunk_when_applicable(self, rng):
        result = select_finish_type(
            layup=60, driving_dunk=50, standing_dunk=75,
            acrobatic_finish=50, post_hook=40, vertical_leap=80,
            speed=60, defender_distance=2.0,
            rim_protector_present=False,
            has_contact_finisher=False, has_slithery_finisher=False,
            has_posterizer=False, has_acrobat=False,
            is_putback=True, rng=rng,
        )
        assert result.finish_type == FinishType.PUTBACK_DUNK
        assert result.is_dunk is True

    def test_floater_preferred_with_rim_protector(self):
        """With a rim protector, acrobatic finishers should favor floaters."""
        floater_count = 0
        for i in range(100):
            r = SeededRNG(seed=i)
            result = select_finish_type(
                layup=60, driving_dunk=40, standing_dunk=30,
                acrobatic_finish=85, post_hook=40, vertical_leap=60,
                speed=70, defender_distance=4.0,
                rim_protector_present=True,
                has_contact_finisher=False, has_slithery_finisher=False,
                has_posterizer=False, has_acrobat=True,
                is_putback=False, rng=r,
            )
            if result.finish_type == FinishType.FLOATER:
                floater_count += 1
        assert floater_count > 15  # Should pick floater a decent amount

    def test_dunk_requires_threshold(self, rng):
        """Low dunk rating should not produce dunks."""
        result = select_finish_type(
            layup=80, driving_dunk=30, standing_dunk=25,
            acrobatic_finish=50, post_hook=40, vertical_leap=40,
            speed=60, defender_distance=5.0,
            rim_protector_present=False,
            has_contact_finisher=False, has_slithery_finisher=False,
            has_posterizer=False, has_acrobat=False,
            is_putback=False, rng=rng,
        )
        assert result.is_dunk is False

    def test_posterizer_enables_poster(self):
        """Posterizer badge should enable poster dunks in contested situations."""
        posters = 0
        for i in range(200):
            r = SeededRNG(seed=i)
            result = select_finish_type(
                layup=70, driving_dunk=90, standing_dunk=85,
                acrobatic_finish=60, post_hook=40, vertical_leap=90,
                speed=80, defender_distance=1.5,
                rim_protector_present=False,
                has_contact_finisher=True, has_slithery_finisher=False,
                has_posterizer=True, has_acrobat=False,
                is_putback=False, rng=r,
            )
            if result.is_poster:
                posters += 1
        assert posters > 0  # Should get at least some posters

    def test_contact_finisher_boosts_foul_chance(self, rng):
        with_badge = select_finish_type(
            layup=75, driving_dunk=60, standing_dunk=55,
            acrobatic_finish=65, post_hook=40, vertical_leap=70,
            speed=75, defender_distance=1.5,
            rim_protector_present=False,
            has_contact_finisher=True, has_slithery_finisher=False,
            has_posterizer=False, has_acrobat=False,
            is_putback=False, rng=rng,
        )
        rng2 = SeededRNG(seed=42)
        without_badge = select_finish_type(
            layup=75, driving_dunk=60, standing_dunk=55,
            acrobatic_finish=65, post_hook=40, vertical_leap=70,
            speed=75, defender_distance=1.5,
            rim_protector_present=False,
            has_contact_finisher=False, has_slithery_finisher=False,
            has_posterizer=False, has_acrobat=False,
            is_putback=False, rng=rng2,
        )
        assert with_badge.foul_draw_chance >= without_badge.foul_draw_chance

    def test_all_finish_specs_defined(self):
        for ft in FinishType:
            assert ft in FINISH_SPECS, f"Missing spec for {ft}"
