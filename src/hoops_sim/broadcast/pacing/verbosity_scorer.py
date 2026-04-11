"""Verbosity scorer: decides full/condensed/skipped treatment for each possession.

Distribution targets:
  Full (30%): Big plays, tight games, star moments, scoring runs
  Condensed (40%): Standard plays with brief narration
  Skipped (30%): Routine plays in blowouts, grouped as summaries
"""

from __future__ import annotations

import enum

from hoops_sim.events.game_events import PossessionResult


class VerbosityLevel(enum.Enum):
    """How much narration a possession receives."""

    FULL = "full"
    CONDENSED = "condensed"
    SKIPPED = "skipped"


class VerbosityScorer:
    """Determines the verbosity level for each possession."""

    def __init__(self) -> None:
        self._consecutive_skips = 0
        self._consecutive_full = 0
        self._last_level = VerbosityLevel.CONDENSED

    def score(self, possession: PossessionResult, intensity: float) -> VerbosityLevel:
        """Determine verbosity level based on intensity and context.

        Args:
            possession: The possession result.
            intensity: 0.0-1.0 intensity score.

        Returns:
            VerbosityLevel indicating how much narration to produce.
        """
        level = self._raw_score(possession, intensity)

        # Prevent too many consecutive skips (max 3)
        if level == VerbosityLevel.SKIPPED:
            self._consecutive_skips += 1
            self._consecutive_full = 0
            if self._consecutive_skips > 3:
                level = VerbosityLevel.CONDENSED
                self._consecutive_skips = 0
        elif level == VerbosityLevel.FULL:
            self._consecutive_full += 1
            self._consecutive_skips = 0
            # Prevent too many consecutive full (max 4)
            if self._consecutive_full > 4:
                level = VerbosityLevel.CONDENSED
                self._consecutive_full = 0
        else:
            self._consecutive_skips = 0
            self._consecutive_full = 0

        self._last_level = level
        return level

    def _raw_score(self, p: PossessionResult, intensity: float) -> VerbosityLevel:
        """Raw scoring without consecutive-play adjustments."""
        # Always full narration for high-intensity moments
        if intensity >= 0.65:
            return VerbosityLevel.FULL

        # Always full for scoring runs
        if p.momentum.scoring_run >= 8:
            return VerbosityLevel.FULL

        # Always full for lead changes
        if p.score.lead_changed:
            return VerbosityLevel.FULL

        # Full for dunks, and-ones
        if p.shot and (p.shot.is_dunk or p.shot.is_and_one):
            return VerbosityLevel.FULL

        # Condensed for moderate intensity
        if intensity >= 0.3:
            return VerbosityLevel.CONDENSED

        # Skip routine plays in blowouts
        if p.score.margin > 20 and p.clock.quarter >= 4:
            return VerbosityLevel.SKIPPED

        if intensity < 0.15:
            return VerbosityLevel.SKIPPED

        return VerbosityLevel.CONDENSED
