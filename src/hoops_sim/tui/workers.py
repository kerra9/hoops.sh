"""Simulation worker for async background game simulation.

Runs the GameSimulator in a background thread and posts events
to the UI via Textual messages, keeping the event loop responsive.
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual.message import Message

from hoops_sim.tui.messages import (
    SimCourtUpdate,
    SimGameOver,
    SimNarration,
    SimTick,
)

if TYPE_CHECKING:
    from hoops_sim.engine.simulator import GameSimulator
    from hoops_sim.tui.screens.live_game import LiveGameScreen


class SimulationWorker:
    """Runs game simulation in the background, posting events to the UI.

    The worker steps the simulator one tick at a time, yielding control
    back to the event loop between ticks so the UI stays responsive.
    Speed is controlled externally by adjusting the delay between steps.
    """

    def __init__(self, simulator: GameSimulator) -> None:
        self.simulator = simulator
        self._paused = False
        self._cancelled = False
        self._delay = 1.0  # seconds between ticks (1x speed)

    @property
    def paused(self) -> bool:
        return self._paused

    def pause(self) -> None:
        self._paused = True

    def resume(self) -> None:
        self._paused = False

    def cancel(self) -> None:
        self._cancelled = True

    def set_speed(self, delay: float) -> None:
        """Set the delay between simulation ticks in seconds."""
        self._delay = max(0.0, delay)

    async def run(self, screen: LiveGameScreen) -> None:
        """Run the simulation loop, posting messages to the screen.

        Args:
            screen: The LiveGameScreen that receives simulation events.
        """
        tick_count = 0

        while not self._cancelled and not self.simulator.is_game_over:
            if self._paused:
                await asyncio.sleep(0.05)
                continue

            events = self.simulator.step()
            tick_count += 1

            # Post narration events
            for sim_event in events:
                if sim_event.narration:
                    screen.post_message(SimNarration(event=sim_event.narration))

            # Post game state update
            gs = self.simulator.game_state
            screen.post_message(
                SimTick(
                    home_score=gs.score.home,
                    away_score=gs.score.away,
                    quarter=gs.clock.quarter,
                    game_clock=gs.clock.display,
                    shot_clock=gs.clock.shot_clock_display,
                    is_overtime=gs.clock.is_overtime,
                    momentum=self.simulator.momentum.value,
                )
            )

            # Post court positions if available
            if hasattr(gs, "court_state") and gs.court_state is not None:
                cs = gs.court_state
                offense = [
                    (p.position.x, p.position.y) for p in cs.offensive_players
                ]
                defense = [
                    (p.position.x, p.position.y) for p in cs.defensive_players
                ]
                screen.post_message(
                    SimCourtUpdate(
                        offense=offense,
                        defense=defense,
                        ball_carrier=cs.ball_handler_index,
                    )
                )

            if self._delay > 0:
                await asyncio.sleep(self._delay)
            else:
                # Instant mode: yield to event loop periodically
                if tick_count % 20 == 0:
                    await asyncio.sleep(0)

        # Game over
        gs = self.simulator.game_state
        screen.post_message(
            SimGameOver(
                home_score=gs.score.home,
                away_score=gs.score.away,
            )
        )
