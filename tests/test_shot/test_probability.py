"""Tests for shot probability calculator."""

from __future__ import annotations

from hoops_sim.shot.probability import ShotContext, calculate_shot_probability


class TestShotProbability:
    def test_base_probability(self):
        # S-curve calibration: 80-rated produces ~45-48% base (realistic)
        ctx = ShotContext(base_rating=80)
        prob = calculate_shot_probability(ctx)
        assert 0.35 < prob < 0.60

    def test_higher_rating_higher_prob(self):
        good = calculate_shot_probability(ShotContext(base_rating=90))
        bad = calculate_shot_probability(ShotContext(base_rating=40))
        assert good > bad

    def test_contest_reduces_probability(self):
        open_shot = calculate_shot_probability(ShotContext(
            base_rating=80, contest_quality=0.0,
        ))
        contested = calculate_shot_probability(ShotContext(
            base_rating=80, contest_quality=0.8,
        ))
        assert open_shot > contested

    def test_deadeye_reduces_contest_penalty(self):
        no_badge = calculate_shot_probability(ShotContext(
            base_rating=80, contest_quality=0.7, deadeye_tier=0,
        ))
        with_badge = calculate_shot_probability(ShotContext(
            base_rating=80, contest_quality=0.7, deadeye_tier=4,
        ))
        assert with_badge > no_badge

    def test_fatigue_reduces_probability(self):
        fresh = calculate_shot_probability(ShotContext(
            base_rating=80, energy_pct=1.0,
        ))
        tired = calculate_shot_probability(ShotContext(
            base_rating=80, energy_pct=0.3,
        ))
        assert fresh > tired

    def test_catch_and_shoot_bonus(self):
        normal = calculate_shot_probability(ShotContext(
            base_rating=80, is_catch_and_shoot=False,
        ))
        cas = calculate_shot_probability(ShotContext(
            base_rating=80, is_catch_and_shoot=True, catch_and_shoot_tier=3,
        ))
        assert cas > normal

    def test_off_dribble_penalty(self):
        spot_up = calculate_shot_probability(ShotContext(
            base_rating=80, is_off_dribble=False,
        ))
        off_dribble = calculate_shot_probability(ShotContext(
            base_rating=80, is_off_dribble=True,
        ))
        assert spot_up > off_dribble

    def test_at_rim_boosted(self):
        at_rim = calculate_shot_probability(ShotContext(
            base_rating=80, shot_distance=3.0,
        ))
        mid = calculate_shot_probability(ShotContext(
            base_rating=80, shot_distance=15.0,
        ))
        assert at_rim > mid

    def test_probability_clamped(self):
        # Even terrible shooters have some chance
        low = calculate_shot_probability(ShotContext(
            base_rating=10, contest_quality=1.0, energy_pct=0.1,
        ))
        assert low >= 0.02

        # Even perfect shooters can miss
        high = calculate_shot_probability(ShotContext(
            base_rating=99, energy_pct=1.0, contest_quality=0.0,
            is_catch_and_shoot=True, catch_and_shoot_tier=4,
            is_hot_zone=True, hot_zone_hunter_tier=4,
        ))
        assert high <= 0.98

    def test_corner_specialist(self):
        normal = calculate_shot_probability(ShotContext(
            base_rating=80, is_corner_three=True, corner_specialist_tier=0,
        ))
        specialist = calculate_shot_probability(ShotContext(
            base_rating=80, is_corner_three=True, corner_specialist_tier=4,
        ))
        assert specialist > normal

    def test_clutch_affects_probability(self):
        clutch_good = calculate_shot_probability(ShotContext(
            base_rating=80, is_clutch=True, clutch_rating=95,
        ))
        clutch_bad = calculate_shot_probability(ShotContext(
            base_rating=80, is_clutch=True, clutch_rating=20,
        ))
        assert clutch_good > clutch_bad
