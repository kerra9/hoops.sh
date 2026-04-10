"""Possession-level narration composer.

Collects all events within a single possession and produces a coherent
multi-sentence description. This is the biggest single change from the
old narration engine: instead of isolated one-line templates, we compose
full possession narratives of 3-8 sentences.
"""

from __future__ import annotations

from typing import List, Optional

from hoops_sim.narration.events import (
    BaseNarrationEvent,
    NarrationEventType,
)
from hoops_sim.narration.narrative_arc import ArcSnapshot
from hoops_sim.narration.play_by_play import PlayByPlayNarrator
from hoops_sim.narration.color_commentary import ColorCommentaryNarrator


class PossessionNarration:
    """The output of narrating a single possession."""

    def __init__(self) -> None:
        self.pbp_lines: List[str] = []
        self.color_lines: List[str] = []

    def add_pbp(self, text: str) -> None:
        if text:
            self.pbp_lines.append(text)

    def add_color(self, text: str) -> None:
        if text:
            self.color_lines.append(text)

    @property
    def has_content(self) -> bool:
        return bool(self.pbp_lines or self.color_lines)

    def full_text(self) -> str:
        """Compose the full narration combining PBP and color."""
        parts = []
        if self.pbp_lines:
            parts.append(" ".join(self.pbp_lines))
        if self.color_lines:
            parts.append(" ".join(self.color_lines))
        return "\n".join(parts)

    def tagged_text(self) -> str:
        """Compose with [PBP] and [COLOR] tags for broadcast format."""
        parts = []
        if self.pbp_lines:
            parts.append(f"[PBP] {' '.join(self.pbp_lines)}")
        if self.color_lines:
            parts.append(f"[COLOR] {' '.join(self.color_lines)}")
        return "\n\n".join(parts)


class PossessionNarrator:
    """Composes full possession narratives from event streams.

    Collects events for a possession, then produces a multi-sentence
    narration combining play-by-play and color commentary with proper
    pacing.
    """

    def __init__(
        self,
        pbp: PlayByPlayNarrator,
        color: ColorCommentaryNarrator,
    ) -> None:
        self.pbp = pbp
        self.color = color
        self._current_events: List[BaseNarrationEvent] = []
        self._possession_count = 0

    def start_possession(self) -> None:
        """Reset for a new possession."""
        self._current_events = []
        self._possession_count += 1

    def add_event(self, event: BaseNarrationEvent) -> None:
        """Add an event to the current possession's event stream."""
        self._current_events.append(event)

    def compose(self, arc_snapshot: ArcSnapshot) -> PossessionNarration:
        """Compose the full possession narration from accumulated events.

        Filters which events get narrated to maintain good pacing:
        - Always narrate shot results, turnovers, blocks
        - Narrate dribble moves only if they led to the play
        - Narrate screens if they set up the action
        - Add color commentary on notable plays
        """
        narration = PossessionNarration()

        # Determine which events are significant enough to narrate
        significant = self._filter_significant_events()

        for event in significant:
            pbp_text = self.pbp.narrate(event)
            narration.add_pbp(pbp_text or "")

            # Color commentary on select events
            if self.color.should_interject(event):
                color_text = self.color.generate(event, arc_snapshot)
                narration.add_color(color_text or "")

        return narration

    def _filter_significant_events(self) -> List[BaseNarrationEvent]:
        """Filter events to the ones worth narrating.

        Strategy:
        - Terminal events (shots, turnovers, blocks) always narrate
        - The 1-2 most recent setup events (dribble, screen, pass) narrate
        - Ball advance narrates if it's the only thing happening
        - Dead ball events (fouls, FTs, subs, timeouts) always narrate
        """
        if not self._current_events:
            return []

        # Always-narrate event types
        always_narrate = {
            NarrationEventType.SHOT_RESULT,
            NarrationEventType.TURNOVER,
            NarrationEventType.BLOCK,
            NarrationEventType.FOUL,
            NarrationEventType.FREE_THROW,
            NarrationEventType.SUBSTITUTION,
            NarrationEventType.TIMEOUT,
            NarrationEventType.QUARTER_EVENT,
            NarrationEventType.REBOUND,
            NarrationEventType.MOMENTUM,
            NarrationEventType.MILESTONE,
        }

        # Setup event types (pick most recent 2)
        setup_types = {
            NarrationEventType.DRIBBLE_MOVE,
            NarrationEventType.SCREEN_ACTION,
            NarrationEventType.PASS_ACTION,
            NarrationEventType.DRIVE,
            NarrationEventType.BALL_ADVANCE,
        }

        result: List[BaseNarrationEvent] = []
        setup_events: List[BaseNarrationEvent] = []

        for event in self._current_events:
            if event.event_type in always_narrate:
                result.append(event)
            elif event.event_type in setup_types:
                setup_events.append(event)

        # Include last 2-3 setup events to build narrative flow
        max_setup = 3 if self._possession_count % 3 == 0 else 2
        recent_setup = setup_events[-max_setup:] if setup_events else []

        # Filter out ball advance if there are better events
        if len(recent_setup) > 1:
            recent_setup = [
                e for e in recent_setup
                if e.event_type != NarrationEventType.BALL_ADVANCE
            ] or recent_setup[-1:]

        # Combine: setup first, then terminal events
        return recent_setup + result

    def compose_dead_ball(self, events: List[BaseNarrationEvent]) -> PossessionNarration:
        """Compose narration for dead ball events (between possessions)."""
        narration = PossessionNarration()
        for event in events:
            pbp_text = self.pbp.narrate(event)
            narration.add_pbp(pbp_text or "")
        return narration
