"""Tests for the runtime court state module."""

from __future__ import annotations

import pytest

from hoops_sim.engine.court_state import (
    BallState,
    BallStatus,
    CourtState,
    PlayerCourtState,
    create_initial_positions,
)
from hoops_sim.models.player import Player, Position
from hoops_sim.models.attributes import PlayerAttributes, AthleticAttributes
from hoops_sim.physical.energy import EnergyState
from hoops_sim.physics.vec import Vec2


def _make_player(pid: int, name: str = "Test", pos: Position = Position.SF) -> Player:
    """Create a minimal test player."""
    return Player(
        id=pid,
        first_name=name,
        last_name=f"Player{pid}",
        position=pos,
        attributes=PlayerAttributes(
            athleticism=AthleticAttributes(speed=70, stamina=70),
        ),
    )


def _make_roster(start_id: int = 1, count: int = 10) -> list[Player]:
    """Create a test roster with `count` players."""
    positions = [Position.PG, Position.SG, Position.SF, Position.PF, Position.C]
    return [
        _make_player(start_id + i, pos=positions[i % 5])
        for i in range(count)
    ]


class TestBallState:
    def test_default_is_dead(self):
        ball = BallState()
        assert ball.status == BallStatus.DEAD
        assert ball.holder_id is None

    def test_held_state(self):
        ball = BallState(status=BallStatus.HELD, holder_id=1)
        assert ball.status == BallStatus.HELD
        assert ball.holder_id == 1


class TestPlayerCourtState:
    def test_player_id(self):
        player = _make_player(42)
        pcs = PlayerCourtState(player=player)
        assert pcs.player_id == 42

    def test_default_not_on_court(self):
        pcs = PlayerCourtState(player=_make_player(1))
        assert pcs.is_on_court is False
        assert pcs.fouls == 0
        assert pcs.minutes_played == 0.0


class TestCourtState:
    def test_ball_handler_returns_none_when_dead(self):
        court = CourtState()
        assert court.ball_handler() is None

    def test_ball_handler_returns_player_when_held(self):
        player = _make_player(1)
        pcs = PlayerCourtState(player=player, is_on_court=True)
        court = CourtState(
            home_on_court=[pcs],
            ball=BallState(status=BallStatus.HELD, holder_id=1),
        )
        handler = court.ball_handler()
        assert handler is not None
        assert handler.player_id == 1

    def test_get_player_state(self):
        p1 = PlayerCourtState(player=_make_player(10), is_on_court=True)
        p2 = PlayerCourtState(player=_make_player(20), is_on_court=True)
        court = CourtState(home_on_court=[p1], away_on_court=[p2])
        assert court.get_player_state(10) is p1
        assert court.get_player_state(20) is p2
        assert court.get_player_state(99) is None

    def test_offensive_defensive_players(self):
        home = [PlayerCourtState(player=_make_player(i)) for i in range(1, 6)]
        away = [PlayerCourtState(player=_make_player(i)) for i in range(6, 11)]
        court = CourtState(home_on_court=home, away_on_court=away)

        assert court.offensive_players(home_on_offense=True) == home
        assert court.defensive_players(home_on_offense=True) == away
        assert court.offensive_players(home_on_offense=False) == away
        assert court.defensive_players(home_on_offense=False) == home

    def test_swap_sides(self):
        court = CourtState(home_attacks_right=True)
        assert court.attacking_right(home_on_offense=True) is True
        court.swap_sides()
        assert court.attacking_right(home_on_offense=True) is False

    def test_closest_defender_to(self):
        off = PlayerCourtState(
            player=_make_player(1), position=Vec2(70, 25), is_on_court=True,
        )
        d1 = PlayerCourtState(
            player=_make_player(10), position=Vec2(72, 25), is_on_court=True,
        )
        d2 = PlayerCourtState(
            player=_make_player(11), position=Vec2(80, 25), is_on_court=True,
        )
        court = CourtState(
            home_on_court=[off], away_on_court=[d1, d2],
        )
        closest = court.closest_defender_to(off.position, home_on_offense=True)
        assert closest is not None
        assert closest.player_id == 10

    def test_distance_to_basket(self):
        player = _make_player(1)
        pcs = PlayerCourtState(
            player=player, position=Vec2(80, 25), is_on_court=True,
        )
        court = CourtState(
            home_on_court=[pcs], home_attacks_right=True,
        )
        dist = court.distance_to_basket(1, home_on_offense=True)
        # Right basket is at ~88.75, 25; from 80,25 that's ~8.75
        assert 8.0 < dist < 10.0


class TestCreateInitialPositions:
    def test_creates_5_on_court_per_team(self):
        home_roster = _make_roster(1, 10)
        away_roster = _make_roster(101, 10)
        court = create_initial_positions(home_roster, away_roster)

        assert len(court.home_on_court) == 5
        assert len(court.away_on_court) == 5
        assert len(court.home_bench) == 5
        assert len(court.away_bench) == 5

    def test_players_on_court_flagged(self):
        home_roster = _make_roster(1, 8)
        away_roster = _make_roster(101, 8)
        court = create_initial_positions(home_roster, away_roster)

        for pcs in court.home_on_court:
            assert pcs.is_on_court is True
        for pcs in court.home_bench:
            assert pcs.is_on_court is False

    def test_defensive_assignments_set(self):
        home_roster = _make_roster(1, 5)
        away_roster = _make_roster(101, 5)
        court = create_initial_positions(home_roster, away_roster)

        for pcs in court.home_on_court:
            assert pcs.defensive_assignment_id is not None
        for pcs in court.away_on_court:
            assert pcs.defensive_assignment_id is not None

    def test_energy_initialized(self):
        home_roster = _make_roster(1, 5)
        away_roster = _make_roster(101, 5)
        court = create_initial_positions(home_roster, away_roster)

        for pcs in court.all_on_court():
            assert pcs.energy.pct > 0.99  # Should be fully charged

    def test_small_roster_works(self):
        home_roster = _make_roster(1, 5)
        away_roster = _make_roster(101, 5)
        court = create_initial_positions(home_roster, away_roster)
        assert len(court.home_on_court) == 5
        assert len(court.home_bench) == 0
