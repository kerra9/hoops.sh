"""Broadcast director: orchestrates all broadcast subsystems.

Consumes an EventStream and produces final broadcast text.
This is the main entry point for the narration layer.

Data flow:
  EventStream -> BroadcastDirector -> IntensityEngine -> VerbosityScorer
    -> ProseComposer / ColorVoice -> Final text
"""

from __future__ import annotations

import random
from typing import List, Optional

from hoops_sim.broadcast.composer.intensity import IntensityEngine
from hoops_sim.broadcast.composer.prose_composer import ProseComposer
from hoops_sim.broadcast.pacing.verbosity_scorer import VerbosityLevel, VerbosityScorer
from hoops_sim.broadcast.segments.game_segments import GameSegments
from hoops_sim.broadcast.stats.live_tracker import BroadcastStatTracker
from hoops_sim.broadcast.voices.color_voice import ColorVoice
from hoops_sim.events.event_stream import EventStream, GameEvent, GameEventType
from hoops_sim.events.game_events import PossessionResult


class BroadcastDirector:
    """Orchestrates the entire broadcast pipeline.

    Takes an EventStream and produces a list of broadcast lines.
    """

    def __init__(
        self,
        home_team: str,
        away_team: str,
        rng: Optional[random.Random] = None,
    ) -> None:
        self._rng = rng or random.Random()
        self._home = home_team
        self._away = away_team

        # Subsystems
        self.intensity = IntensityEngine()
        self.composer = ProseComposer(self._rng)
        self.verbosity = VerbosityScorer()
        self.color = ColorVoice(self._rng)
        self.segments = GameSegments(home_team, away_team, self._rng)
        self.stats = BroadcastStatTracker(home_team, away_team)

        # State
        self._lines: List[str] = []
        self._skip_buffer: List[PossessionResult] = []

    def broadcast_game(self, stream: EventStream) -> List[str]:
        """Process an entire event stream and return broadcast lines.

        Args:
            stream: The complete event stream from a simulated game.

        Returns:
            Ordered list of broadcast text lines.
        """
        self._lines = []

        for event in stream:
            self._process_event(event)

        # Flush any remaining skip buffer
        self._flush_skip_buffer()

        return self._lines

    def broadcast_possession(self, possession: PossessionResult) -> List[str]:
        """Process a single possession and return broadcast lines.

        For use in step-by-step simulation (TUI mode).
        """
        lines: List[str] = []

        # Score intensity
        intensity = self.intensity.score(possession)

        # Determine verbosity
        level = self.verbosity.score(possession, intensity)

        # Update stat tracking
        self.stats.process_possession(possession)

        if level == VerbosityLevel.SKIPPED:
            self._skip_buffer.append(possession)
            if len(self._skip_buffer) >= 4:
                summary = self._summarize_skipped()
                if summary:
                    lines.append(summary)
            return lines

        # Flush skip buffer if we're transitioning to non-skip
        if self._skip_buffer:
            summary = self._summarize_skipped()
            if summary:
                lines.append(summary)

        if level == VerbosityLevel.CONDENSED:
            prose = self.composer.compose(possession, intensity)
            if prose:
                lines.append(prose)
        else:
            # Full narration
            prose = self.composer.compose(possession, intensity)
            if prose:
                lines.append(prose)

            # Color commentary for notable+ plays
            if intensity >= 0.5 and possession.ball_handler:
                p_stats = self.stats.get_player_stats(possession.ball_handler.id)
                color = self.color.comment(
                    possession,
                    intensity,
                    player_points=p_stats.points,
                    player_field_goals=p_stats.field_goals_made,
                    player_threes=p_stats.threes_made,
                )
                if color:
                    lines.append(color)

        return lines

    def _process_event(self, event: GameEvent) -> None:
        """Process a single game event."""
        if event.event_type == GameEventType.GAME_START:
            self._lines.append(self.segments.game_open())

        elif event.event_type == GameEventType.QUARTER_START:
            q = event.data.get("quarter", 1)
            if q > 1:
                home = event.data.get("home_score", 0)
                away = event.data.get("away_score", 0)
                intro = self.segments.quarter_intro(q, home, away)
                if intro:
                    self._lines.append(intro)

        elif event.event_type == GameEventType.HALFTIME:
            home = event.data.get("home_score", 0)
            away = event.data.get("away_score", 0)
            self._lines.append(self.segments.halftime_report(home, away))

        elif event.event_type == GameEventType.QUARTER_END:
            pass  # Quarter end is handled by quarter start of next

        elif event.event_type == GameEventType.POSSESSION:
            if event.possession:
                lines = self.broadcast_possession(event.possession)
                self._lines.extend(lines)

        elif event.event_type == GameEventType.GAME_END:
            self._flush_skip_buffer()
            home = event.data.get("home_score", 0)
            away = event.data.get("away_score", 0)
            self._lines.append(self.segments.game_end(home, away))

    def _flush_skip_buffer(self) -> None:
        """Flush skipped possessions as a summary line."""
        if self._skip_buffer:
            summary = self._summarize_skipped()
            if summary:
                self._lines.append(summary)

    def _summarize_skipped(self) -> str:
        """Generate a summary for skipped possessions."""
        if not self._skip_buffer:
            return ""

        count = len(self._skip_buffer)
        buffer = self._skip_buffer
        self._skip_buffer = []

        # Count scores in skipped possessions
        scores = [p for p in buffer if p.scored]

        if not scores:
            return ""

        if count <= 2:
            parts = []
            for p in scores:
                if p.shot and p.shot.made and p.ball_handler:
                    name = p.ball_handler.name.split()[-1] if p.ball_handler.name else "?"
                    if p.shot.points == 3:
                        parts.append(f"{name} with a three")
                    else:
                        parts.append(f"{name} scores")
            if parts:
                return "Both teams trade baskets. " + ", ".join(parts) + "."
            return ""

        # Larger skip: just summarize the score change
        last = buffer[-1]
        score = last.score
        return (
            f"Teams trade baskets over the next few possessions. "
            f"{score.home_team} {score.home_score_after}, "
            f"{score.away_team} {score.away_score_after}."
        )
