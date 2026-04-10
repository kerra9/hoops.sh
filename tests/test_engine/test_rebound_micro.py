"""Tests for micro-action rebound simulation."""

from __future__ import annotations

import pytest

from hoops_sim.engine.rebound import (
    ReboundCandidate,
    ReboundResult,
    ReboundType,
    determine_rebound_location,
    resolve_rebound,
)
from hoops_sim.physics.vec import Vec2
from hoops_sim.utils.rng import SeededRNG


@pytest.fixture
def rng():
    return SeededRNG(seed=42)


class TestReboundLocation:
    def test_air_ball_gives_side_rebound(self, rng):
        reb_type, pos = determine_rebound_location(
            shot_distance=25.0, is_three=True,
            rim_result="air_ball", basket_position=Vec2(88.75, 25.0),
            rng=rng,
        )
        assert reb_type == ReboundType.SIDE

    def test_front_rim_gives_short(self, rng):
        reb_type, pos = determine_rebound_location(
            shot_distance=15.0, is_three=False,
            rim_result="front", basket_position=Vec2(88.75, 25.0),
            rng=rng,
        )
        assert reb_type == ReboundType.SHORT

    def test_back_rim_gives_long(self, rng):
        reb_type, pos = determine_rebound_location(
            shot_distance=24.0, is_three=True,
            rim_result="back", basket_position=Vec2(88.75, 25.0),
            rng=rng,
        )
        assert reb_type == ReboundType.LONG

    def test_rim_out_gives_random(self, rng):
        reb_type, pos = determine_rebound_location(
            shot_distance=18.0, is_three=False,
            rim_result="rim_out", basket_position=Vec2(88.75, 25.0),
            rng=rng,
        )
        assert reb_type == ReboundType.RIM_OUT


class TestReboundResolution:
    def _make_candidate(self, player_id, pos, reb=70, is_offense=False):
        return ReboundCandidate(
            player_id=player_id, position=pos,
            height_inches=80, vertical_leap=70,
            rebound_rating=reb, box_out_rating=65,
            hustle=70, is_boxed_out=False,
            is_offense=is_offense, crash_boards_tendency=0.5,
        )

    def test_resolve_returns_result(self, rng):
        candidates = [
            self._make_candidate(1, Vec2(87.0, 25.0)),
            self._make_candidate(2, Vec2(88.0, 26.0)),
        ]
        result = resolve_rebound(
            candidates=candidates,
            rebound_position=Vec2(88.0, 25.0),
            rebound_type=ReboundType.SHORT,
            rng=rng,
        )
        assert isinstance(result, ReboundResult)
        assert result.rebounder_id in (1, 2)

    def test_closer_player_more_likely(self):
        close_wins = 0
        for i in range(200):
            r = SeededRNG(seed=i)
            candidates = [
                ReboundCandidate(
                    player_id=1, position=Vec2(88.0, 25.0),
                    height_inches=80, vertical_leap=70,
                    rebound_rating=70, box_out_rating=65,
                    hustle=70, is_boxed_out=False,
                    is_offense=False, crash_boards_tendency=0.5,
                ),
                ReboundCandidate(
                    player_id=2, position=Vec2(75.0, 25.0),  # Much farther
                    height_inches=80, vertical_leap=70,
                    rebound_rating=70, box_out_rating=65,
                    hustle=70, is_boxed_out=False,
                    is_offense=False, crash_boards_tendency=0.5,
                ),
            ]
            result = resolve_rebound(
                candidates=candidates,
                rebound_position=Vec2(88.0, 25.5),
                rebound_type=ReboundType.SHORT, rng=r,
            )
            if result and result.rebounder_id == 1:
                close_wins += 1
        assert close_wins > 100  # Closer player should win majority

    def test_no_candidates_returns_none(self, rng):
        result = resolve_rebound([], Vec2(88.0, 25.0), ReboundType.SHORT, rng)
        assert result is None

    def test_boxed_out_penalty(self):
        """Boxed-out players should win less often."""
        free_wins = 0
        for i in range(200):
            r = SeededRNG(seed=i)
            candidates = [
                ReboundCandidate(
                    player_id=1, position=Vec2(88.0, 25.0),
                    height_inches=80, vertical_leap=70,
                    rebound_rating=70, box_out_rating=65,
                    hustle=70, is_boxed_out=True,  # Boxed out
                    is_offense=True, crash_boards_tendency=0.8,
                ),
                ReboundCandidate(
                    player_id=2, position=Vec2(88.0, 25.5),
                    height_inches=80, vertical_leap=70,
                    rebound_rating=70, box_out_rating=65,
                    hustle=70, is_boxed_out=False,  # Free
                    is_offense=False, crash_boards_tendency=0.5,
                ),
            ]
            result = resolve_rebound(
                candidates=candidates,
                rebound_position=Vec2(88.0, 25.0),
                rebound_type=ReboundType.SHORT, rng=r,
            )
            if result and result.rebounder_id == 2:
                free_wins += 1
        assert free_wins > 100  # Free player should dominate
