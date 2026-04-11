"""Event stream: ordered collection of game events for broadcast consumption.

The simulation appends events here. The broadcast director reads them.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, List, Optional

from hoops_sim.events.game_events import PossessionResult


class GameEventType(enum.Enum):
    """Types of events in the game stream."""

    POSSESSION = "possession"
    QUARTER_START = "quarter_start"
    QUARTER_END = "quarter_end"
    HALFTIME = "halftime"
    GAME_START = "game_start"
    GAME_END = "game_end"
    TIMEOUT = "timeout"
    SUBSTITUTION = "substitution"


@dataclass
class GameEvent:
    """A single event in the game stream."""

    event_type: GameEventType
    possession: Optional[PossessionResult] = None
    data: dict = field(default_factory=dict)
    quarter: int = 1
    game_clock: float = 720.0

    @property
    def is_possession(self) -> bool:
        return self.event_type == GameEventType.POSSESSION


class EventStream:
    """Ordered collection of game events.

    The simulation appends events. The broadcast director iterates them.
    """

    def __init__(self) -> None:
        self._events: List[GameEvent] = []

    def append(self, event: GameEvent) -> None:
        """Add an event to the stream."""
        self._events.append(event)

    def append_possession(self, result: PossessionResult) -> None:
        """Convenience: append a possession result as a GameEvent."""
        self._events.append(GameEvent(
            event_type=GameEventType.POSSESSION,
            possession=result,
            quarter=result.clock.quarter,
            game_clock=result.clock.game_clock,
        ))

    def append_quarter_start(self, quarter: int) -> None:
        self._events.append(GameEvent(
            event_type=GameEventType.QUARTER_START,
            data={"quarter": quarter},
            quarter=quarter,
        ))

    def append_quarter_end(self, quarter: int, home_score: int, away_score: int) -> None:
        self._events.append(GameEvent(
            event_type=GameEventType.QUARTER_END,
            data={"quarter": quarter, "home_score": home_score, "away_score": away_score},
            quarter=quarter,
        ))

    def append_halftime(self, home_score: int, away_score: int) -> None:
        self._events.append(GameEvent(
            event_type=GameEventType.HALFTIME,
            data={"home_score": home_score, "away_score": away_score},
            quarter=2,
        ))

    def append_game_end(self, home_score: int, away_score: int) -> None:
        self._events.append(GameEvent(
            event_type=GameEventType.GAME_END,
            data={"home_score": home_score, "away_score": away_score},
        ))

    def __len__(self) -> int:
        return len(self._events)

    def __iter__(self):
        return iter(self._events)

    def __getitem__(self, index):
        return self._events[index]

    @property
    def possessions(self) -> List[PossessionResult]:
        """Return all possession results in order."""
        return [
            e.possession for e in self._events
            if e.is_possession and e.possession is not None
        ]

    @property
    def last_possession(self) -> Optional[PossessionResult]:
        """Return the most recent possession result."""
        for e in reversed(self._events):
            if e.is_possession and e.possession is not None:
                return e.possession
        return None

    def recent_possessions(self, count: int = 10) -> List[PossessionResult]:
        """Return the N most recent possession results."""
        results = []
        for e in reversed(self._events):
            if e.is_possession and e.possession is not None:
                results.append(e.possession)
                if len(results) >= count:
                    break
        results.reverse()
        return results
