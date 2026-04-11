"""Clock-aware narration -- shot clock urgency and game clock drama.

Real broadcasts reference the clock constantly. This module generates
clock-context phrases that get injected into the chain composer output
as urgency modifiers.
"""

from __future__ import annotations

from enum import Enum
from typing import List, Optional

from hoops_sim.utils.rng import SeededRNG


class IntensityLevel(Enum):
    """Game situation intensity from the clock/score perspective."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAXIMUM = "maximum"


class ClockNarrator:
    """Generates clock-aware urgency phrases and situation context.

    Tracks shot clock, game clock, quarter, and score differential
    to inject appropriate urgency and context into narration.
    """

    def __init__(self, rng: SeededRNG) -> None:
        self.rng = rng

    def shot_clock_phrase(self, shot_clock: float) -> Optional[str]:
        """Generate a shot clock urgency phrase, if warranted.

        Returns None if the shot clock isn't noteworthy.
        """
        if shot_clock > 7.0:
            return None

        if shot_clock <= 3.0:
            return self.rng.choice([
                "Running out of time!",
                "Has to get something up!",
                f"Only {shot_clock:.0f} on the shot clock!",
                "Shot clock about to expire!",
            ])

        if shot_clock <= 5.0:
            return self.rng.choice([
                f"Shot clock at {shot_clock:.0f}...",
                f"{shot_clock:.0f} on the shot clock, has to make a move...",
                "Shot clock winding down...",
                f"Under {shot_clock:.0f} seconds to get a shot up...",
            ])

        # 5-7 seconds
        return self.rng.choice([
            "Shot clock getting low...",
            "Clock ticking...",
            f"{shot_clock:.0f} on the shot clock...",
        ])

    def game_clock_phrase(
        self,
        quarter: int,
        game_clock: float,
        score_diff: int,
    ) -> Optional[str]:
        """Generate a game clock situation phrase.

        Only returns something for noteworthy clock situations:
        late in quarters, clutch time, etc.
        """
        minutes = int(game_clock // 60)
        seconds = int(game_clock % 60)
        clock_str = f"{minutes}:{seconds:02d}"

        # 4th quarter / OT, under 2 minutes, close game
        if quarter >= 4 and game_clock < 120.0 and abs(score_diff) <= 5:
            if game_clock < 30:
                return self.rng.choice([
                    f"{game_clock:.0f} seconds left...",
                    f"Under 30 seconds, {'down' if score_diff < 0 else 'up'} {abs(score_diff)}...",
                    f"{game_clock:.0f} ticks remaining...",
                ])
            return self.rng.choice([
                f"{clock_str} left in the {'4th' if quarter == 4 else 'overtime'}...",
                f"Under {minutes + 1} minutes, {'trailing' if score_diff < 0 else 'leading'} by {abs(score_diff)}...",
                f"We're under two minutes. {'Down' if score_diff < 0 else 'Up'} {abs(score_diff)}.",
            ])

        # 4th quarter, under 5 minutes, within 10
        if quarter >= 4 and game_clock < 300.0 and abs(score_diff) <= 10:
            if self.rng.random() < 0.3:
                return self.rng.choice([
                    f"{clock_str} to go in the 4th...",
                    f"Under {minutes + 1} minutes left...",
                ])

        # End of any quarter (last 30 seconds)
        if game_clock < 30.0:
            if self.rng.random() < 0.5:
                q_name = _quarter_name(quarter)
                return f"Winding down in the {q_name}..."

        # Halftime approaching
        if quarter == 2 and game_clock < 60.0:
            if self.rng.random() < 0.3:
                return "Last minute of the half..."

        return None

    def clutch_shot_modifier(
        self,
        quarter: int,
        game_clock: float,
        score_diff: int,
        points: int,
    ) -> Optional[str]:
        """Generate a modifier for clutch-situation shots.

        Returns extra phrases like 'to TIE IT' or 'to take the lead'
        when the score situation is dramatic.
        """
        if quarter < 4:
            return None

        if game_clock > 120.0:
            return None

        new_diff = score_diff + points

        if score_diff < 0 and new_diff == 0:
            return "to TIE IT"
        if score_diff < 0 and new_diff > 0:
            return "to take the LEAD"
        if score_diff <= 0 and new_diff > 0 and game_clock < 30:
            return f"with {game_clock:.0f} seconds to go"
        if abs(score_diff) <= 3 and game_clock < 60:
            return f"with {game_clock:.0f} seconds left"

        return None

    def intensity_level(
        self,
        quarter: int,
        game_clock: float,
        score_diff: int,
    ) -> IntensityLevel:
        """Compute the game situation intensity level.

        Maps (quarter, time_remaining, score_differential) to an
        intensity that drives template selection and announcer energy.
        """
        abs_diff = abs(score_diff)

        # Q4 or OT, under 2 min, within 5
        if quarter >= 4 and game_clock < 120.0 and abs_diff <= 5:
            return IntensityLevel.MAXIMUM

        # Q4, under 5 min, within 10
        if quarter >= 4 and game_clock < 300.0 and abs_diff <= 10:
            return IntensityLevel.HIGH

        # Close game any quarter
        if abs_diff <= 5 and quarter >= 3:
            return IntensityLevel.HIGH

        # Blowout
        if abs_diff >= 25:
            return IntensityLevel.LOW

        # Q1-Q3 general
        if quarter <= 2:
            return IntensityLevel.LOW

        return IntensityLevel.MEDIUM


def _quarter_name(quarter: int) -> str:
    """Convert quarter number to display name."""
    names = {1: "1st", 2: "2nd", 3: "3rd", 4: "4th"}
    return names.get(quarter, f"OT{quarter - 4}")
