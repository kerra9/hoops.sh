"""Tests for the event contract dataclasses."""

import pytest

from hoops_sim.events.game_events import (
    ActionChainResult,
    ClockSnapshot,
    MoveResult,
    PlayerRef,
    PossessionResult,
    ScoreSnapshot,
    ShotResult,
    TurnoverResult,
    FoulResult,
    ViolationResult,
    MomentumSnapshot,
)


class TestPlayerRef:
    def test_basic_creation(self):
        ref = PlayerRef(id=1, name="Marcus Williams", team="Celtics", jersey=7)
        assert ref.id == 1
        assert ref.name == "Marcus Williams"
        assert ref.team == "Celtics"
        assert ref.jersey == 7

    def test_optional_fields(self):
        ref = PlayerRef(
            id=1, name="Marcus Williams", team="Celtics",
            nickname="The Maestro", signature_move="step-back three",
        )
        assert ref.nickname == "The Maestro"
        assert ref.signature_move == "step-back three"


class TestClockSnapshot:
    def test_auto_time_description(self):
        snap = ClockSnapshot(quarter=4, game_clock=90.0)
        assert snap.time_description == "under 2 minutes"

    def test_early_clock(self):
        snap = ClockSnapshot(quarter=1, game_clock=600.0)
        assert snap.time_description == "early in the quarter"

    def test_clutch(self):
        snap = ClockSnapshot(quarter=4, game_clock=90.0, is_clutch=True)
        assert snap.is_clutch is True


class TestScoreSnapshot:
    def test_lead_team(self):
        s = ScoreSnapshot(
            home_team="Celtics", away_team="Knicks",
            home_score=50, away_score=48,
            home_score_after=52, away_score_after=48,
        )
        assert s.lead_team == "Celtics"
        assert s.margin == 4

    def test_tie_game(self):
        s = ScoreSnapshot(
            home_team="Celtics", away_team="Knicks",
            home_score_after=50, away_score_after=50,
        )
        assert s.is_tie is True
        assert s.lead_team == ""

    def test_lead_changed(self):
        s = ScoreSnapshot(
            home_team="Celtics", away_team="Knicks",
            home_score=48, away_score=50,
            home_score_after=51, away_score_after=50,
        )
        assert s.lead_changed is True


class TestPossessionResult:
    def test_exactly_one_terminal_shot(self):
        p = PossessionResult(
            shot=ShotResult(made=True, points=2),
        )
        p.validate()
        assert p.terminal_type == "shot"

    def test_exactly_one_terminal_turnover(self):
        p = PossessionResult(
            turnover=TurnoverResult(turnover_type="steal"),
        )
        p.validate()
        assert p.terminal_type == "turnover"

    def test_zero_terminal_events_raises(self):
        p = PossessionResult()
        with pytest.raises(ValueError, match="no terminal event"):
            p.validate()

    def test_multiple_terminal_events_raises(self):
        p = PossessionResult(
            shot=ShotResult(made=True, points=2),
            turnover=TurnoverResult(turnover_type="steal"),
        )
        with pytest.raises(ValueError, match="2 terminal events"):
            p.validate()

    def test_scored_property(self):
        # Made shot
        p = PossessionResult(shot=ShotResult(made=True, points=3))
        assert p.scored is True
        assert p.points_scored == 3

        # Missed shot
        p2 = PossessionResult(shot=ShotResult(made=False, points=0))
        assert p2.scored is False
        assert p2.points_scored == 0

        # Free throws
        p3 = PossessionResult(foul=FoulResult(free_throws_made=2))
        assert p3.scored is True
        assert p3.points_scored == 2


class TestActionChainResult:
    def test_chain_with_moves(self):
        chain = ActionChainResult(
            player=PlayerRef(id=1, name="Test", team="A"),
            defender=PlayerRef(id=2, name="Def", team="B"),
            moves=[
                MoveResult(move_type="crossover", success=True, defender_reaction="bites", separation_gained=1.5),
                MoveResult(move_type="hesitation", success=True, defender_reaction="stays_home", separation_gained=0.5),
            ],
            total_separation=2.0,
            outcome="separation",
        )
        assert len(chain.moves) == 2
        assert chain.total_separation == 2.0
        assert chain.outcome == "separation"
