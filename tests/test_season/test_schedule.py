"""Tests for schedule generation."""

from __future__ import annotations

import pytest

from hoops_sim.season.schedule import ScheduledGame, SeasonSchedule, generate_schedule
from hoops_sim.utils.rng import SeededRNG


class TestScheduledGame:
    def test_record_result(self):
        g = ScheduledGame(game_id=1, home_team_id=1, away_team_id=2)
        g.record_result(110, 105)
        assert g.played
        assert g.winner_id == 1
        assert g.home_score == 110


class TestGenerateSchedule:
    def test_generates_games(self):
        schedule = generate_schedule([1, 2, 3, 4], games_per_team=10, rng=SeededRNG(42))
        assert len(schedule.games) > 0

    def test_each_team_plays(self):
        schedule = generate_schedule([1, 2, 3, 4, 5, 6], games_per_team=10, rng=SeededRNG(42))
        for tid in [1, 2, 3, 4, 5, 6]:
            games = schedule.team_games(tid)
            assert len(games) > 0

    def test_games_on_day(self):
        schedule = generate_schedule([1, 2, 3, 4], games_per_team=10, rng=SeededRNG(42))
        day1 = schedule.games_on_day(1)
        assert len(day1) > 0

    def test_games_remaining(self):
        schedule = generate_schedule([1, 2, 3, 4], games_per_team=10, rng=SeededRNG(42))
        total = schedule.games_remaining(1)
        assert total > 0
        
        # Play a game
        game = schedule.next_unplayed(1)
        assert game is not None
        game.record_result(100, 95)
        assert schedule.games_remaining(1) == total - 1

    def test_deterministic(self):
        s1 = generate_schedule([1, 2, 3], games_per_team=6, rng=SeededRNG(42))
        s2 = generate_schedule([1, 2, 3], games_per_team=6, rng=SeededRNG(42))
        assert len(s1.games) == len(s2.games)
        for g1, g2 in zip(s1.games, s2.games):
            assert g1.home_team_id == g2.home_team_id
            assert g1.away_team_id == g2.away_team_id
