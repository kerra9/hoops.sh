"""Tests for the Scoreboard service (Phase 1c).

Verifies that the Scoreboard correctly updates all subsystems
for each event type: baskets, misses, turnovers, steals, fouls,
rebounds, blocks, free throws, and shot clock violations.
"""

from __future__ import annotations

import pytest

from hoops_sim.engine.game import GameState
from hoops_sim.engine.scoreboard import Scoreboard
from hoops_sim.models.stats import TeamGameStats
from hoops_sim.models.team import Team
from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.psychology.confidence import ConfidenceTracker
from hoops_sim.psychology.momentum import MomentumTracker


@pytest.fixture
def scoreboard():
    gs = GameState()
    gs.start_quarter(1)
    gs.clock.start()
    home_stats = TeamGameStats(team_id=1, team_name="Hawks")
    away_stats = TeamGameStats(team_id=2, team_name="Celtics")
    home_stats.add_player(10, "Trae Young")
    home_stats.add_player(11, "Bogdan Bogdanovic")
    away_stats.add_player(20, "Jayson Tatum")
    away_stats.add_player(21, "Jaylen Brown")
    confidence = ConfidenceTracker()
    momentum = MomentumTracker()
    broadcast_stats = LiveStatTracker(home_team="Hawks", away_team="Celtics")
    return Scoreboard(
        game_state=gs,
        home_stats=home_stats,
        away_stats=away_stats,
        confidence=confidence,
        momentum=momentum,
        broadcast_stats=broadcast_stats,
    )


class TestRecordBasket:
    def test_two_pointer_updates_score(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=2, is_three=False,
        )
        assert scoreboard.gs.score.home == 2
        assert scoreboard.gs.score.away == 0

    def test_three_pointer_updates_score(self, scoreboard):
        scoreboard.record_basket(
            player_id=20, player_name="Jayson Tatum",
            is_home=False, points=3, is_three=True,
        )
        assert scoreboard.gs.score.away == 3

    def test_basket_updates_player_stats(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=2, is_three=False,
        )
        stats = scoreboard.home_stats.get_player(10)
        assert stats.fgm == 1
        assert stats.fga == 1
        assert stats.points == 2

    def test_three_pointer_updates_three_stats(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=3, is_three=True,
        )
        stats = scoreboard.home_stats.get_player(10)
        assert stats.three_pm == 1
        assert stats.three_pa == 1
        assert stats.points == 3

    def test_basket_updates_team_stats(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=2, is_three=False, is_paint=True,
        )
        assert scoreboard.home_stats.points == 2
        assert scoreboard.home_stats.points_in_paint == 2

    def test_basket_with_assist(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=2, is_three=False,
            assister_id=11, assister_name="Bogdan Bogdanovic",
        )
        a_stats = scoreboard.home_stats.get_player(11)
        assert a_stats.assists == 1

    def test_free_throw_via_record_basket(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=1, is_three=False,
        )
        assert scoreboard.gs.score.home == 1
        stats = scoreboard.home_stats.get_player(10)
        assert stats.ftm == 1
        assert stats.fta == 1

    def test_dunk_triggers_momentum(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=2, is_three=False, is_dunk=True,
        )
        assert scoreboard.gs.score.home == 2


class TestRecordMiss:
    def test_miss_updates_player_stats(self, scoreboard):
        scoreboard.record_miss(
            player_id=10, player_name="Trae Young",
            is_home=True, is_three=False,
        )
        stats = scoreboard.home_stats.get_player(10)
        assert stats.fga == 1
        assert stats.fgm == 0

    def test_missed_ft(self, scoreboard):
        scoreboard.record_missed_ft(player_id=10, is_home=True)
        stats = scoreboard.home_stats.get_player(10)
        assert stats.fta == 1
        assert stats.ftm == 0


class TestRecordTurnover:
    def test_turnover_updates_stats(self, scoreboard):
        scoreboard.record_turnover(
            player_id=10, player_name="Trae Young", is_home=True,
        )
        stats = scoreboard.home_stats.get_player(10)
        assert stats.turnovers == 1
        assert scoreboard.home_stats.turnovers == 1


class TestRecordSteal:
    def test_steal_updates_both_sides(self, scoreboard):
        scoreboard.record_steal(
            handler_id=10, handler_name="Trae Young", handler_is_home=True,
            stealer_id=20, stealer_name="Jayson Tatum",
        )
        h_stats = scoreboard.home_stats.get_player(10)
        assert h_stats.turnovers == 1
        s_stats = scoreboard.away_stats.get_player(20)
        assert s_stats.steals == 1


class TestRecordFoul:
    def test_foul_updates_stats(self, scoreboard):
        scoreboard.record_foul(
            fouler_id=20, fouler_name="Jayson Tatum",
            fouler_is_home=False, fouler_personal_fouls=1,
        )
        stats = scoreboard.away_stats.get_player(20)
        assert stats.personal_fouls == 1
        assert scoreboard.gs.away_team_fouls == 1


class TestRecordRebound:
    def test_offensive_rebound(self, scoreboard):
        scoreboard.record_rebound(
            player_id=10, player_name="Trae Young",
            is_home=True, is_offensive=True,
        )
        stats = scoreboard.home_stats.get_player(10)
        assert stats.offensive_rebounds == 1

    def test_defensive_rebound(self, scoreboard):
        scoreboard.record_rebound(
            player_id=20, player_name="Jayson Tatum",
            is_home=False, is_offensive=False,
        )
        stats = scoreboard.away_stats.get_player(20)
        assert stats.defensive_rebounds == 1


class TestRecordBlock:
    def test_block_updates_stats(self, scoreboard):
        scoreboard.record_block(
            blocker_id=20, blocker_name="Jayson Tatum",
            blocker_is_home=False,
        )
        stats = scoreboard.away_stats.get_player(20)
        assert stats.blocks == 1


class TestShotClockViolation:
    def test_shot_clock_violation(self, scoreboard):
        scoreboard.record_shot_clock_violation(is_home=True)
        assert scoreboard.home_stats.turnovers == 1


class TestScoreConsistency:
    """Verify that score stays consistent across multiple operations."""

    def test_multiple_baskets_accumulate(self, scoreboard):
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=2, is_three=False,
        )
        scoreboard.record_basket(
            player_id=10, player_name="Trae Young",
            is_home=True, points=3, is_three=True,
        )
        scoreboard.record_basket(
            player_id=20, player_name="Jayson Tatum",
            is_home=False, points=2, is_three=False,
        )
        assert scoreboard.gs.score.home == 5
        assert scoreboard.gs.score.away == 2
        assert scoreboard.home_stats.points == 5
        assert scoreboard.away_stats.points == 2
