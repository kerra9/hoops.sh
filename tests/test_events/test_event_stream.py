"""Tests for the EventStream."""

from hoops_sim.events.event_stream import EventStream, GameEvent, GameEventType
from hoops_sim.events.game_events import (
    PossessionResult,
    ShotResult,
    ClockSnapshot,
    TurnoverResult,
)


class TestEventStream:
    def test_empty_stream(self):
        stream = EventStream()
        assert len(stream) == 0
        assert stream.last_possession is None

    def test_append_possession(self):
        stream = EventStream()
        p = PossessionResult(
            shot=ShotResult(made=True, points=2),
            clock=ClockSnapshot(quarter=1),
        )
        stream.append_possession(p)
        assert len(stream) == 1
        assert stream.last_possession is p

    def test_possessions_property(self):
        stream = EventStream()
        p1 = PossessionResult(shot=ShotResult(made=True, points=2))
        p2 = PossessionResult(turnover=TurnoverResult(turnover_type="steal"))
        stream.append_possession(p1)
        stream.append_quarter_start(2)
        stream.append_possession(p2)
        assert len(stream.possessions) == 2

    def test_recent_possessions(self):
        stream = EventStream()
        for i in range(15):
            p = PossessionResult(shot=ShotResult(made=True, points=2))
            stream.append_possession(p)
        recent = stream.recent_possessions(5)
        assert len(recent) == 5

    def test_append_structural_events(self):
        stream = EventStream()
        stream.append_quarter_start(1)
        stream.append_quarter_end(1, 28, 24)
        stream.append_halftime(52, 48)
        stream.append_game_end(110, 105)
        assert len(stream) == 4

    def test_iteration(self):
        stream = EventStream()
        stream.append_quarter_start(1)
        p = PossessionResult(shot=ShotResult(made=True, points=2))
        stream.append_possession(p)
        events = list(stream)
        assert len(events) == 2
        assert events[0].event_type == GameEventType.QUARTER_START
        assert events[1].event_type == GameEventType.POSSESSION
