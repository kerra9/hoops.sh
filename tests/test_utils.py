"""Tests for utility modules: RNG, math helpers."""

from __future__ import annotations

import pytest

from hoops_sim.utils.math import attribute_to_range, clamp, inverse_lerp, lerp, remap
from hoops_sim.utils.rng import RNGManager, SeededRNG


class TestClamp:
    def test_within_range(self):
        assert clamp(5.0, 0.0, 10.0) == 5.0

    def test_below_range(self):
        assert clamp(-5.0, 0.0, 10.0) == 0.0

    def test_above_range(self):
        assert clamp(15.0, 0.0, 10.0) == 10.0


class TestLerp:
    def test_zero(self):
        assert lerp(0.0, 10.0, 0.0) == pytest.approx(0.0)

    def test_one(self):
        assert lerp(0.0, 10.0, 1.0) == pytest.approx(10.0)

    def test_half(self):
        assert lerp(0.0, 10.0, 0.5) == pytest.approx(5.0)

    def test_clamped(self):
        assert lerp(0.0, 10.0, 1.5) == pytest.approx(10.0)
        assert lerp(0.0, 10.0, -0.5) == pytest.approx(0.0)


class TestInverseLerp:
    def test_basic(self):
        assert inverse_lerp(0.0, 10.0, 5.0) == pytest.approx(0.5)

    def test_at_bounds(self):
        assert inverse_lerp(0.0, 10.0, 0.0) == pytest.approx(0.0)
        assert inverse_lerp(0.0, 10.0, 10.0) == pytest.approx(1.0)

    def test_clamped(self):
        assert inverse_lerp(0.0, 10.0, 15.0) == pytest.approx(1.0)

    def test_equal_bounds(self):
        assert inverse_lerp(5.0, 5.0, 5.0) == pytest.approx(0.0)


class TestRemap:
    def test_basic(self):
        assert remap(5.0, 0.0, 10.0, 0.0, 100.0) == pytest.approx(50.0)

    def test_different_ranges(self):
        assert remap(50.0, 0.0, 100.0, 0.0, 1.0) == pytest.approx(0.5)


class TestAttributeToRange:
    def test_min_attribute(self):
        assert attribute_to_range(0, 18.0, 28.0) == pytest.approx(18.0)

    def test_max_attribute(self):
        assert attribute_to_range(99, 18.0, 28.0) == pytest.approx(28.0)

    def test_mid_attribute(self):
        result = attribute_to_range(50, 18.0, 28.0)
        assert 22.0 < result < 24.0


class TestSeededRNG:
    def test_deterministic(self):
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=42)
        assert rng1.random() == rng2.random()

    def test_different_seeds_different(self):
        rng1 = SeededRNG(seed=42)
        rng2 = SeededRNG(seed=99)
        # Very unlikely to be equal
        assert rng1.random() != rng2.random()

    def test_gauss(self):
        rng = SeededRNG(seed=42)
        values = [rng.gauss(0, 1) for _ in range(1000)]
        mean = sum(values) / len(values)
        assert abs(mean) < 0.2  # Should be near 0

    def test_uniform(self):
        rng = SeededRNG(seed=42)
        for _ in range(100):
            val = rng.uniform(5.0, 10.0)
            assert 5.0 <= val <= 10.0

    def test_randint(self):
        rng = SeededRNG(seed=42)
        for _ in range(100):
            val = rng.randint(1, 6)
            assert 1 <= val <= 6

    def test_choice(self):
        rng = SeededRNG(seed=42)
        items = ["a", "b", "c"]
        result = rng.choice(items)
        assert result in items

    def test_fork_deterministic(self):
        rng = SeededRNG(seed=42)
        child1 = rng.fork("physics")
        rng2 = SeededRNG(seed=42)
        child2 = rng2.fork("physics")
        assert child1.random() == child2.random()

    def test_fork_independent(self):
        rng = SeededRNG(seed=42)
        child_a = rng.fork("physics")
        child_b = rng.fork("ai")
        # Different streams should produce different values
        # (not guaranteed but extremely likely with different seeds)
        vals_a = [child_a.random() for _ in range(10)]
        vals_b = [child_b.random() for _ in range(10)]
        assert vals_a != vals_b


class TestRNGManager:
    def test_named_streams(self):
        mgr = RNGManager(master_seed=42)
        physics = mgr.physics
        ai = mgr.ai
        assert physics is not ai

    def test_same_stream_returned(self):
        mgr = RNGManager(master_seed=42)
        a = mgr.get_stream("test")
        b = mgr.get_stream("test")
        assert a is b

    def test_deterministic(self):
        mgr1 = RNGManager(master_seed=42)
        mgr2 = RNGManager(master_seed=42)
        assert mgr1.physics.random() == mgr2.physics.random()
