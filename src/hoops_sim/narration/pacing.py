"""Dynamic pacing and verbosity engine.

Not every possession deserves the same word count. A transition layup
gets 15 words. A clutch three with 30 seconds left gets 80. This module
scores each possession's verbosity from 0.0-1.0 and enforces natural
rhythm variation across the game.
"""

from __future__ import annotations

from collections import deque
from typing import Deque, List, Optional

from hoops_sim.narration.clock_narrator import IntensityLevel, ClockNarrator
from hoops_sim.narration.events import (
    BaseNarrationEvent,
    NarrationEventType,
)
from hoops_sim.narration.narrative_arc import ArcSnapshot


class VerbosityBand:
    """Maps a verbosity score to a word-count range and style."""

    LOW = (0.0, 0.3)       # 15-25 words, terse
    MEDIUM = (0.3, 0.6)    # 25-50 words, standard
    HIGH = (0.6, 0.8)      # 50-80 words, detailed + color
    MAXIMUM = (0.8, 1.0)   # 80-120 words, everything narrated

    @staticmethod
    def label(score: float) -> str:
        if score < 0.3:
            return "LOW"
        if score < 0.6:
            return "MEDIUM"
        if score < 0.8:
            return "HIGH"
        return "MAXIMUM"


class PacingManager:
    """Scores possession verbosity and enforces pacing rhythm.

    Factors:
    - Game clock situation (25%)
    - Score differential context (20%)
    - Play complexity (15%)
    - Narrative arc intensity (15%)
    - Momentum magnitude (10%)
    - Player significance (10%)
    - Consecutive quiet possessions (5%)
    """

    def __init__(
        self,
        clock_narrator: Optional[ClockNarrator] = None,
    ) -> None:
        self.clock_narrator = clock_narrator
        self._recent_scores: Deque[float] = deque(maxlen=10)
        self._consecutive_low = 0
        self._consecutive_high = 0

    def score_verbosity(
        self,
        events: List[BaseNarrationEvent],
        arc_snapshot: ArcSnapshot,
    ) -> float:
        """Score the current possession's verbosity from 0.0 to 1.0.

        Combines multiple factors and applies rhythm smoothing.
        """
        if not events:
            return 0.3

        # Use the last event's clock/score data for situation assessment
        last = events[-1]
        quarter = last.quarter
        game_clock = last.game_clock
        score_diff = last.home_score - last.away_score

        # Factor 1: Game clock situation (0.25 weight)
        clock_score = self._clock_factor(quarter, game_clock, score_diff)

        # Factor 2: Score differential context (0.20 weight)
        diff_score = self._diff_factor(score_diff, quarter)

        # Factor 3: Play complexity (0.15 weight)
        complexity = self._complexity_factor(events)

        # Factor 4: Narrative arc intensity (0.15 weight)
        arc_score = 0.3
        if arc_snapshot.has_active_arc and arc_snapshot.primary_arc:
            arc_score = arc_snapshot.primary_arc.intensity

        # Factor 5: Momentum magnitude (0.10 weight)
        momentum = self._momentum_factor(events)

        # Factor 6: Player significance (0.10 weight)
        significance = self._significance_factor(events)

        # Factor 7: Consecutive quiet possessions (0.05 weight)
        quiet_boost = min(1.0, self._consecutive_low * 0.15)

        raw = (
            clock_score * 0.25
            + diff_score * 0.20
            + complexity * 0.15
            + arc_score * 0.15
            + momentum * 0.10
            + significance * 0.10
            + quiet_boost * 0.05
        )

        # Apply rhythm control
        smoothed = self._apply_rhythm(raw)

        self._recent_scores.append(smoothed)
        return max(0.0, min(1.0, smoothed))

    def _clock_factor(
        self, quarter: int, game_clock: float, score_diff: int,
    ) -> float:
        """Score based on game clock situation."""
        if self.clock_narrator:
            intensity = self.clock_narrator.intensity_level(
                quarter, game_clock, score_diff,
            )
            mapping = {
                IntensityLevel.LOW: 0.2,
                IntensityLevel.MEDIUM: 0.5,
                IntensityLevel.HIGH: 0.75,
                IntensityLevel.MAXIMUM: 1.0,
            }
            return mapping[intensity]

        # Fallback without clock narrator
        if quarter >= 4 and game_clock < 120.0:
            return 0.9
        if quarter >= 4 and game_clock < 300.0:
            return 0.6
        return 0.3

    def _diff_factor(self, score_diff: int, quarter: int) -> float:
        """Score based on score differential."""
        abs_diff = abs(score_diff)
        if abs_diff <= 3:
            return 0.8
        if abs_diff <= 8:
            return 0.5
        if abs_diff <= 15:
            return 0.3
        return 0.1  # Blowout -- low verbosity

    def _complexity_factor(self, events: List[BaseNarrationEvent]) -> float:
        """Score based on how many micro-actions occurred."""
        setup_count = sum(
            1 for e in events
            if e.event_type in {
                NarrationEventType.DRIBBLE_MOVE,
                NarrationEventType.SCREEN_ACTION,
                NarrationEventType.PASS_ACTION,
                NarrationEventType.DRIVE,
            }
        )
        # More actions = more complex = higher verbosity
        if setup_count >= 4:
            return 0.9
        if setup_count >= 2:
            return 0.6
        if setup_count >= 1:
            return 0.4
        return 0.2

    def _momentum_factor(self, events: List[BaseNarrationEvent]) -> float:
        """Score based on momentum events in the possession."""
        has_momentum = any(
            e.event_type == NarrationEventType.MOMENTUM for e in events
        )
        return 0.8 if has_momentum else 0.3

    def _significance_factor(self, events: List[BaseNarrationEvent]) -> float:
        """Score based on notable player events."""
        has_milestone = any(
            e.event_type == NarrationEventType.MILESTONE for e in events
        )
        return 0.8 if has_milestone else 0.3

    def _apply_rhythm(self, raw: float) -> float:
        """Apply rhythm smoothing to avoid monotonous pacing.

        After 2-3 high possessions, force a lower one.
        After 3+ low possessions, boost the next interesting one.
        """
        if raw >= 0.6:
            self._consecutive_high += 1
            self._consecutive_low = 0
        elif raw < 0.3:
            self._consecutive_low += 1
            self._consecutive_high = 0
        else:
            self._consecutive_high = 0
            self._consecutive_low = 0

        # Force a breather after 3 consecutive high possessions
        if self._consecutive_high >= 3 and raw < 0.9:
            return raw * 0.6

        # Boost after 3+ quiet possessions
        if self._consecutive_low >= 3 and raw >= 0.3:
            return min(1.0, raw * 1.3)

        return raw

    @property
    def average_recent_verbosity(self) -> float:
        """Average verbosity of recent possessions."""
        if not self._recent_scores:
            return 0.5
        return sum(self._recent_scores) / len(self._recent_scores)
