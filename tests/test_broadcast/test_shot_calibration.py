"""Tests for the shot probability S-curve calibration."""

from hoops_sim.shot.probability import ShotContext, calculate_shot_probability


class TestShotCalibration:
    def test_s_curve_base_probabilities(self):
        """Verify the S-curve produces realistic base probabilities."""
        # 50-rated should be around 35%
        ctx_50 = ShotContext(base_rating=50, shot_distance=15.0)
        prob_50 = calculate_shot_probability(ctx_50)
        assert 0.25 < prob_50 < 0.45, f"50-rated: {prob_50:.2%}"

        # 70-rated should be around 43%
        ctx_70 = ShotContext(base_rating=70, shot_distance=15.0)
        prob_70 = calculate_shot_probability(ctx_70)
        assert 0.33 < prob_70 < 0.53, f"70-rated: {prob_70:.2%}"

        # 80-rated should be around 48%
        ctx_80 = ShotContext(base_rating=80, shot_distance=15.0)
        prob_80 = calculate_shot_probability(ctx_80)
        assert 0.38 < prob_80 < 0.58, f"80-rated: {prob_80:.2%}"

        # 99-rated should be around 58%
        ctx_99 = ShotContext(base_rating=99, shot_distance=15.0)
        prob_99 = calculate_shot_probability(ctx_99)
        assert 0.45 < prob_99 < 0.68, f"99-rated: {prob_99:.2%}"

    def test_lower_than_old_system(self):
        """New S-curve should produce lower probabilities than the old linear system."""
        # Old system: base_rating / 100.0 (80-rated = 0.80 base)
        # New system: should be much lower
        ctx = ShotContext(base_rating=80, shot_distance=15.0)
        prob = calculate_shot_probability(ctx)
        # Should be well below 80%
        assert prob < 0.60

    def test_contest_penalty_increased(self):
        """Contested shots should be harder (penalty increased from 0.35 to 0.50)."""
        open_ctx = ShotContext(base_rating=80, contest_quality=0.0)
        contested_ctx = ShotContext(base_rating=80, contest_quality=1.0)
        open_prob = calculate_shot_probability(open_ctx)
        contested_prob = calculate_shot_probability(contested_ctx)
        # Contested should be at least 40% worse
        assert contested_prob < open_prob * 0.65

    def test_off_dribble_penalty_increased(self):
        """Off-dribble shots should be harder (penalty increased from 0.92 to 0.85)."""
        catch_ctx = ShotContext(base_rating=80, is_off_dribble=False)
        dribble_ctx = ShotContext(base_rating=80, is_off_dribble=True)
        catch_prob = calculate_shot_probability(catch_ctx)
        dribble_prob = calculate_shot_probability(dribble_ctx)
        # Off-dribble should be at least 12% worse
        assert dribble_prob < catch_prob * 0.90

    def test_probability_bounds(self):
        """Probability should always be clamped to 0.02-0.98."""
        # Very low
        low_ctx = ShotContext(base_rating=1, contest_quality=1.0, energy_pct=0.1, shot_distance=30.0)
        assert calculate_shot_probability(low_ctx) >= 0.02

        # Very high
        high_ctx = ShotContext(base_rating=99, shot_distance=2.0, is_catch_and_shoot=True)
        assert calculate_shot_probability(high_ctx) <= 0.98

    def test_monotonic_with_rating(self):
        """Higher ratings should produce higher probabilities, all else equal."""
        probs = []
        for rating in [30, 50, 70, 80, 90, 99]:
            ctx = ShotContext(base_rating=rating, shot_distance=15.0)
            probs.append(calculate_shot_probability(ctx))
        for i in range(len(probs) - 1):
            assert probs[i] < probs[i + 1], f"Rating progression not monotonic at index {i}"
