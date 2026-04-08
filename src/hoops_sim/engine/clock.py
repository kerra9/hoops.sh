"""Game clock and shot clock management."""

from __future__ import annotations

from dataclasses import dataclass

from hoops_sim.utils.constants import (
    OVERTIME_LENGTH_MINUTES,
    QUARTER_LENGTH_MINUTES,
    SHOT_CLOCK_OFFENSIVE_REBOUND,
    SHOT_CLOCK_SECONDS,
    TICK_DURATION,
)


@dataclass
class GameClock:
    """Manages game clock and shot clock.

    Time is tracked in seconds with 0.1s resolution.
    """

    quarter: int = 1
    game_clock: float = QUARTER_LENGTH_MINUTES * 60.0  # Counts down
    shot_clock: float = SHOT_CLOCK_SECONDS  # Counts down
    is_running: bool = False
    is_overtime: bool = False

    @property
    def minutes_remaining(self) -> int:
        return int(self.game_clock // 60)

    @property
    def seconds_remaining(self) -> float:
        return round(self.game_clock % 60, 1)

    @property
    def display(self) -> str:
        """Clock display like '8:24.3'."""
        mins = int(self.game_clock // 60)
        secs = self.game_clock % 60
        return f"{mins}:{secs:04.1f}"

    @property
    def shot_clock_display(self) -> str:
        """Shot clock display."""
        if self.shot_clock >= 10:
            return str(int(self.shot_clock))
        return f"{self.shot_clock:.1f}"

    def tick(self, dt: float = TICK_DURATION) -> None:
        """Advance the clocks by dt seconds."""
        if not self.is_running:
            return

        self.game_clock = max(0.0, self.game_clock - dt)
        self.shot_clock = max(0.0, self.shot_clock - dt)

    def start(self) -> None:
        """Start the clock."""
        self.is_running = True

    def stop(self) -> None:
        """Stop the clock (dead ball, foul, out of bounds, etc.)."""
        self.is_running = False

    def reset_shot_clock(self, full: bool = True) -> None:
        """Reset the shot clock.

        Args:
            full: If True, reset to 24. If False, reset to 14 (offensive rebound).
        """
        if full:
            new_val = float(SHOT_CLOCK_SECONDS)
        else:
            new_val = float(SHOT_CLOCK_OFFENSIVE_REBOUND)
        # Shot clock can't exceed game clock
        self.shot_clock = min(new_val, self.game_clock)

    def is_shot_clock_violation(self) -> bool:
        """Check if the shot clock has expired."""
        return self.shot_clock <= 0.0 and self.is_running

    def is_quarter_over(self) -> bool:
        """Check if the game clock has reached 0."""
        return self.game_clock <= 0.0

    def start_quarter(self, quarter: int) -> None:
        """Set up for a new quarter."""
        self.quarter = quarter
        if quarter <= 4:
            self.game_clock = QUARTER_LENGTH_MINUTES * 60.0
            self.is_overtime = False
        else:
            self.game_clock = OVERTIME_LENGTH_MINUTES * 60.0
            self.is_overtime = True
        self.shot_clock = float(SHOT_CLOCK_SECONDS)
        self.is_running = False

    def is_clutch_time(self) -> bool:
        """Check if we're in clutch time (last 2 minutes of 4th quarter or OT)."""
        return (self.quarter >= 4) and (self.game_clock <= 120.0)

    def is_last_two_minutes(self) -> bool:
        """Check if we're in the last 2 minutes of any quarter."""
        return self.game_clock <= 120.0
