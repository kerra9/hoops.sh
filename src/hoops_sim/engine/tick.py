"""Master tick loop at 0.1-second resolution.

The tick engine is the heart of the simulation. Every 0.1 seconds, it:
1. Advances the game clock
2. Updates all player positions (movement layer)
3. Processes ball physics
4. Checks for events (shot clock violation, quarter end)
5. Returns any events that occurred during this tick
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Optional

from hoops_sim.engine.clock import GameClock
from hoops_sim.engine.game import GamePhase, GameState
from hoops_sim.engine.possession import PossessionState
from hoops_sim.utils.constants import TICK_DURATION


class TickEventType(enum.Enum):
    """Events that can occur during a tick."""

    NONE = "none"
    SHOT_CLOCK_VIOLATION = "shot_clock_violation"
    QUARTER_END = "quarter_end"
    GAME_END = "game_end"
    MADE_BASKET = "made_basket"
    MISSED_SHOT = "missed_shot"
    FOUL = "foul"
    TURNOVER = "turnover"
    TIMEOUT = "timeout"
    SUBSTITUTION = "substitution"
    JUMP_BALL = "jump_ball"
    OUT_OF_BOUNDS = "out_of_bounds"


@dataclass
class TickEvent:
    """An event that occurred during a tick."""

    event_type: TickEventType
    tick_number: int
    description: str = ""
    data: dict = field(default_factory=dict)


@dataclass
class TickResult:
    """Result of processing a single tick."""

    tick_number: int
    dt: float
    events: List[TickEvent] = field(default_factory=list)
    clock_running: bool = True


class TickEngine:
    """The master tick loop that drives the simulation.

    Processes one tick at a time, advancing the game state.
    """

    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state
        self.tick_number = 0
        self.dt = TICK_DURATION

    def process_tick(self) -> TickResult:
        """Process a single simulation tick.

        Returns:
            TickResult with any events that occurred.
        """
        self.tick_number += 1
        events: List[TickEvent] = []
        gs = self.game_state

        # Only advance clock when the ball is live
        if gs.possession.is_live():
            gs.clock.tick(self.dt)

        # Advance possession tick counter
        gs.possession.tick()

        # Check shot clock violation
        if gs.clock.is_shot_clock_violation() and gs.possession.is_live():
            events.append(TickEvent(
                event_type=TickEventType.SHOT_CLOCK_VIOLATION,
                tick_number=self.tick_number,
                description="Shot clock violation",
            ))
            gs.clock.stop()
            gs.possession.transition_to(PossessionState.DEAD_BALL)

        # Check quarter end
        if gs.clock.is_quarter_over() and gs.possession.is_live():
            events.append(TickEvent(
                event_type=TickEventType.QUARTER_END,
                tick_number=self.tick_number,
                description=f"End of quarter {gs.clock.quarter}",
            ))
            gs.clock.stop()
            gs.possession.transition_to(PossessionState.END_OF_QUARTER)

        return TickResult(
            tick_number=self.tick_number,
            dt=self.dt,
            events=events,
            clock_running=gs.clock.is_running,
        )

    def run_ticks(self, count: int) -> List[TickResult]:
        """Run multiple ticks.

        Args:
            count: Number of ticks to process.

        Returns:
            List of TickResults.
        """
        results = []
        for _ in range(count):
            results.append(self.process_tick())
        return results
