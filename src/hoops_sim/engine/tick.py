"""Master tick loop at 0.1-second resolution.

The tick engine is the heart of the simulation. Every 0.1 seconds, it:
1. Advances the game clock
2. Updates all player positions (movement layer) via callbacks
3. Processes ball physics via callbacks
4. Checks for events (shot clock violation, quarter end)
5. Returns any events that occurred during this tick

Phase 9: Extended with callback hooks and variable-dt advance() so the
simulator can delegate all clock/event management to this single engine.
"""

from __future__ import annotations

import enum
import math
from collections.abc import Callable
from dataclasses import dataclass, field

from hoops_sim.engine.game import GameState
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
    events: list[TickEvent] = field(default_factory=list)
    clock_running: bool = True


class TickEngine:
    """The master tick loop that drives the simulation.

    Processes one tick at a time, advancing the game state.
    Supports callback hooks so subsystems (FSMs, energy, contact detection)
    can be registered without the engine knowing about them directly.
    """

    def __init__(self, game_state: GameState) -> None:
        self.game_state = game_state
        self.tick_number = 0
        self.dt = TICK_DURATION

        # Callback hooks -- registered by the simulator or other systems
        self._on_tick_callbacks: list[Callable[[float], None]] = []

    def register_on_tick(self, callback: Callable[[float], None]) -> None:
        """Register a callback that fires every tick.

        The callback receives the dt (time step) as its argument.
        Use this to hook in FSM updates, energy drain, contact detection, etc.
        """
        self._on_tick_callbacks.append(callback)

    def clear_callbacks(self) -> None:
        """Remove all registered callbacks."""
        self._on_tick_callbacks.clear()

    def process_tick(self, dt_override: float | None = None) -> TickResult:
        """Process a single simulation tick.

        Args:
            dt_override: Optional custom time step. Defaults to TICK_DURATION.

        Returns:
            TickResult with any events that occurred.
        """
        dt = dt_override if dt_override is not None else self.dt
        self.tick_number += 1
        events: list[TickEvent] = []
        gs = self.game_state

        # Only advance clock when the ball is live
        if gs.possession.is_live():
            gs.clock.tick(dt)

        # Advance possession tick counter
        gs.possession.tick()

        # Fire registered callbacks (FSMs, energy, contact detection)
        for callback in self._on_tick_callbacks:
            callback(dt)

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
            dt=dt,
            events=events,
            clock_running=gs.clock.is_running,
        )

    def advance(self, seconds: float) -> list[TickEvent]:
        """Advance by an arbitrary number of seconds.

        Decomposes the time into fixed-dt sub-ticks so all registered
        callbacks fire at the correct frequency. The last sub-tick may
        be shorter than dt if seconds is not evenly divisible.

        Args:
            seconds: Total time to advance (e.g. 2.5 for a drive).

        Returns:
            All TickEvents that occurred during the advance.
        """
        all_events: list[TickEvent] = []
        remaining = seconds
        while remaining > 1e-9:
            step = min(self.dt, remaining)
            result = self.process_tick(dt_override=step)
            all_events.extend(result.events)
            remaining -= step
        return all_events

    def run_ticks(self, count: int) -> list[TickResult]:
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
