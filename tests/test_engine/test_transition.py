"""Tests for transition and fast break evaluation."""

from __future__ import annotations

import pytest

from hoops_sim.engine.transition import (
    TransitionAdvantage,
    TransitionEvaluation,
    evaluate_transition,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


@pytest.fixture
def rng():
    return SeededRNG(seed=42)


class TestTransition:
    def test_no_advantage_returns_5v5(self, rng):
        basket = Vec2(88.75, 25.0)
        result = evaluate_transition(
            rebounder_speed=60,
            rebounder_transition_tendency=0.3,
            offense_positions=[
                (1, Vec2(50.0, 25.0), 70),
                (2, Vec2(45.0, 15.0), 65),
                (3, Vec2(48.0, 35.0), 60),
            ],
            defense_positions=[
                (11, Vec2(70.0, 20.0), 70),
                (12, Vec2(72.0, 30.0), 65),
                (13, Vec2(68.0, 25.0), 75),
                (14, Vec2(75.0, 15.0), 60),
            ],
            basket_position=basket,
            is_steal=False,
            rng=rng,
        )
        assert isinstance(result, TransitionEvaluation)

    def test_steal_more_likely_to_push(self, rng):
        basket = Vec2(88.75, 25.0)
        result = evaluate_transition(
            rebounder_speed=80,
            rebounder_transition_tendency=0.5,
            offense_positions=[
                (1, Vec2(70.0, 25.0), 80),
                (2, Vec2(75.0, 15.0), 75),
            ],
            defense_positions=[
                (11, Vec2(50.0, 25.0), 60),
            ],
            basket_position=basket,
            is_steal=True,
            rng=rng,
        )
        assert result.should_push is True
        assert result.scoring_chance > 0.3

    def test_scoring_chance_increases_with_advantage(self, rng):
        basket = Vec2(88.75, 25.0)
        # 2v1 situation
        result = evaluate_transition(
            rebounder_speed=80,
            rebounder_transition_tendency=0.7,
            offense_positions=[
                (1, Vec2(70.0, 25.0), 80),
                (2, Vec2(75.0, 15.0), 75),
                (3, Vec2(80.0, 35.0), 70),
            ],
            defense_positions=[
                (11, Vec2(85.0, 25.0), 60),
            ],
            basket_position=basket,
            is_steal=True,
            rng=rng,
        )
        assert result.scoring_chance > 0.5
