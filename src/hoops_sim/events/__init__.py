"""Event contract: pure dataclasses that form the boundary between simulation and narration.

The simulation layer produces these events. The broadcast layer consumes them.
Neither layer imports from the other -- this package is the interface.
"""

from hoops_sim.events.game_events import (
    ActionChainResult,
    ClockSnapshot,
    DriveResult,
    FoulResult,
    MomentumSnapshot,
    MoveResult,
    PassResult,
    PlayerRef,
    PossessionResult,
    ReboundResult,
    ScoreSnapshot,
    ScreenResult,
    ShotResult,
    TurnoverResult,
    ViolationResult,
)
from hoops_sim.events.event_stream import EventStream, GameEvent, GameEventType

__all__ = [
    "ActionChainResult",
    "ClockSnapshot",
    "DriveResult",
    "EventStream",
    "FoulResult",
    "GameEvent",
    "GameEventType",
    "MomentumSnapshot",
    "MoveResult",
    "PassResult",
    "PlayerRef",
    "PossessionResult",
    "ReboundResult",
    "ScoreSnapshot",
    "ScreenResult",
    "ShotResult",
    "TurnoverResult",
    "ViolationResult",
]
