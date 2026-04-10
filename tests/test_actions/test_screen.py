"""Tests for screen mechanics."""

from __future__ import annotations

import pytest

from hoops_sim.actions.screen import (
    ScreenResult,
    ScreenType,
    evaluate_screen,
)
from hoops_sim.utils.rng import SeededRNG


@pytest.fixture
def rng():
    return SeededRNG(seed=42)


class TestScreenMechanics:
    def test_evaluate_screen_returns_result(self, rng):
        result = evaluate_screen(
            screen_type=ScreenType.BALL_SCREEN,
            screener_strength=80,
            screener_weight=240.0,
            screener_screen_rating=75,
            defender_strength=60,
            defender_weight=200.0,
            is_stationary=True,
            moving_screen_detection=0.3,
            rng=rng,
        )
        assert isinstance(result, ScreenResult)
        assert result.screen_type == ScreenType.BALL_SCREEN
        assert 0.0 < result.quality <= 1.0
        assert result.separation_created > 0

    def test_stationary_screen_is_legal(self, rng):
        result = evaluate_screen(
            screen_type=ScreenType.BALL_SCREEN,
            screener_strength=70, screener_weight=230.0,
            screener_screen_rating=70, defender_strength=65,
            defender_weight=210.0, is_stationary=True,
            moving_screen_detection=0.5, rng=rng,
        )
        assert result.is_legal is True
        assert result.moving_screen_called is False

    def test_moving_screen_not_always_called(self, rng):
        """Moving screens are only called sometimes."""
        called = 0
        for i in range(100):
            r = SeededRNG(seed=i)
            result = evaluate_screen(
                screen_type=ScreenType.BALL_SCREEN,
                screener_strength=70, screener_weight=230.0,
                screener_screen_rating=70, defender_strength=65,
                defender_weight=210.0, is_stationary=False,
                moving_screen_detection=0.5, rng=r,
            )
            if result.moving_screen_called:
                called += 1
        # Should be called roughly 25% of the time (0.5 * 0.5)
        assert 5 < called < 60

    def test_strong_screener_creates_more_separation(self):
        rng1 = SeededRNG(seed=42)
        strong = evaluate_screen(
            screen_type=ScreenType.BALL_SCREEN,
            screener_strength=95, screener_weight=280.0,
            screener_screen_rating=90, defender_strength=50,
            defender_weight=190.0, is_stationary=True,
            moving_screen_detection=0.3, rng=rng1,
        )
        rng2 = SeededRNG(seed=42)
        weak = evaluate_screen(
            screen_type=ScreenType.BALL_SCREEN,
            screener_strength=40, screener_weight=180.0,
            screener_screen_rating=35, defender_strength=80,
            defender_weight=250.0, is_stationary=True,
            moving_screen_detection=0.3, rng=rng2,
        )
        assert strong.quality > weak.quality

    def test_all_screen_types_valid(self, rng):
        for stype in ScreenType:
            result = evaluate_screen(
                screen_type=stype,
                screener_strength=70, screener_weight=230.0,
                screener_screen_rating=70, defender_strength=65,
                defender_weight=210.0, is_stationary=True,
                moving_screen_detection=0.3, rng=rng,
            )
            assert result.separation_created > 0
