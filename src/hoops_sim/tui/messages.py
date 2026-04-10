"""Custom Textual Message classes for simulation events.

These messages flow from the simulation worker to the UI layer,
allowing reactive widget updates without blocking the event loop.
"""

from __future__ import annotations

from dataclasses import dataclass

from textual.message import Message

from hoops_sim.narration.engine import NarrationEvent


class SimTick(Message):
    """Posted every simulation tick with updated game state."""

    def __init__(
        self,
        home_score: int = 0,
        away_score: int = 0,
        quarter: int = 1,
        game_clock: str = "12:00.0",
        shot_clock: str = "24",
        is_overtime: bool = False,
        possession_home: bool = True,
        momentum: float = 0.0,
    ) -> None:
        super().__init__()
        self.home_score = home_score
        self.away_score = away_score
        self.quarter = quarter
        self.game_clock = game_clock
        self.shot_clock = shot_clock
        self.is_overtime = is_overtime
        self.possession_home = possession_home
        self.momentum = momentum


class SimNarration(Message):
    """Posted when new narration text is available."""

    def __init__(self, event: NarrationEvent) -> None:
        super().__init__()
        self.event = event


class SimCourtUpdate(Message):
    """Posted when player positions change on the court."""

    def __init__(
        self,
        offense: list[tuple[float, float]],
        defense: list[tuple[float, float]],
        ball_carrier: int | None = None,
    ) -> None:
        super().__init__()
        self.offense = offense
        self.defense = defense
        self.ball_carrier = ball_carrier


class SimGameOver(Message):
    """Posted when the game ends."""

    def __init__(
        self,
        home_score: int = 0,
        away_score: int = 0,
    ) -> None:
        super().__init__()
        self.home_score = home_score
        self.away_score = away_score


class SimSpeedChanged(Message):
    """Posted when simulation speed changes."""

    def __init__(self, speed_label: str, interval: float) -> None:
        super().__init__()
        self.speed_label = speed_label
        self.interval = interval
