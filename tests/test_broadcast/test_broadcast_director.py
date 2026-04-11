"""Tests for the BroadcastDirector."""

import random

from hoops_sim.broadcast.composer.broadcast_director import BroadcastDirector
from hoops_sim.events.event_stream import EventStream
from hoops_sim.events.game_events import (
    ClockSnapshot,
    MomentumSnapshot,
    PlayerRef,
    PossessionResult,
    ScoreSnapshot,
    ShotResult,
    TurnoverResult,
)


class TestBroadcastDirector:
    def setup_method(self):
        self.director = BroadcastDirector(
            home_team="Celtics", away_team="Knicks",
            rng=random.Random(42),
        )

    def _make_possession(self, quarter=1, gc=400.0, made=True, points=2):
        return PossessionResult(
            ball_handler=PlayerRef(id=1, name="Marcus Williams", team="Celtics"),
            primary_defender=PlayerRef(id=2, name="Jaylen Thompson", team="Knicks"),
            offensive_team="Celtics",
            defensive_team="Knicks",
            shot=ShotResult(
                shooter=PlayerRef(id=1, name="Marcus Williams", team="Celtics"),
                made=made, points=points,
            ),
            clock=ClockSnapshot(quarter=quarter, game_clock=gc),
            score=ScoreSnapshot(
                home_team="Celtics", away_team="Knicks",
                home_score=50, away_score=48,
                home_score_after=50 + (points if made else 0), away_score_after=48,
            ),
            momentum=MomentumSnapshot(),
        )

    def test_broadcast_single_possession(self):
        p = self._make_possession()
        lines = self.director.broadcast_possession(p)
        assert len(lines) >= 1
        assert any("Williams" in line for line in lines)

    def test_broadcast_game_stream(self):
        stream = EventStream()
        stream.append(
            __import__("hoops_sim.events.event_stream", fromlist=["GameEvent"]).GameEvent(
                event_type=__import__("hoops_sim.events.event_stream", fromlist=["GameEventType"]).GameEventType.GAME_START,
            )
        )
        stream.append_quarter_start(1)
        for i in range(5):
            stream.append_possession(self._make_possession())
        stream.append_quarter_end(1, 62, 58)
        stream.append_halftime(62, 58)
        stream.append_game_end(110, 105)

        lines = self.director.broadcast_game(stream)
        assert len(lines) >= 3  # At least game open + some possessions + game end
        # Should have game open
        assert any("tonight" in line.lower() or "welcome" in line.lower() or "matchup" in line.lower() for line in lines)
        # Should have game end
        assert any("FINAL" in line or "final" in line.lower() for line in lines)

    def test_stat_tracking(self):
        for _ in range(5):
            p = self._make_possession(made=True, points=3)
            self.director.broadcast_possession(p)

        stats = self.director.stats.get_player_stats(1)
        assert stats.points == 15
        assert stats.threes_made == 5
