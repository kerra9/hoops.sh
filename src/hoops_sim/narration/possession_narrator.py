"""Possession-level narration composer.

Collects all events within a single possession and produces a coherent
multi-sentence description. Uses importance scoring instead of hard caps
to decide which events to narrate, and feeds events through the
ChainComposer for flowing multi-clause prose.
"""

from __future__ import annotations

from typing import List, Optional, TYPE_CHECKING

from hoops_sim.narration.events import (
    BaseNarrationEvent,
    DribbleMoveEvent,
    DriveEvent,
    NarrationEventType,
    PassEvent,
    ScreenEvent,
)
from hoops_sim.narration.narrative_arc import ArcSnapshot
from hoops_sim.narration.play_by_play import PlayByPlayNarrator
from hoops_sim.narration.color_commentary import ColorCommentaryNarrator

if TYPE_CHECKING:
    from hoops_sim.narration.chain_composer import ChainComposer
    from hoops_sim.narration.pacing import PacingManager


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


def _compute_importance(event: BaseNarrationEvent) -> float:
    """Score an event's narration importance from 0.0 to 1.0.

    Terminal events always get 1.0. Setup events are scored based on
    their type and context so the pipeline keeps rich action chains
    instead of capping at 2-3 events.
    """
    always_max = {
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
        NarrationEventType.STEAL,
    }
    if event.event_type in always_max:
        return 1.0

    if event.event_type == NarrationEventType.DRIBBLE_MOVE:
        score = 0.6
        if isinstance(event, DribbleMoveEvent):
            if event.ankle_breaker:
                score += 0.3
            if event.combo_count >= 2:
                score += 0.1
            if not event.success:
                score += 0.05  # failed moves are still interesting
        return min(1.0, score)

    if event.event_type == NarrationEventType.SCREEN_ACTION:
        score = 0.5
        if isinstance(event, ScreenEvent):
            if event.switch_occurred:
                score += 0.2
            if event.pnr_coverage:
                score += 0.1
        return min(1.0, score)

    if event.event_type == NarrationEventType.PASS_ACTION:
        score = 0.5
        if isinstance(event, PassEvent):
            if event.is_kick_out:
                score += 0.2
            if event.is_skip_pass:
                score += 0.2
            if event.is_entry_pass:
                score += 0.1
        return min(1.0, score)

    if event.event_type == NarrationEventType.DRIVE:
        score = 0.7
        if isinstance(event, DriveEvent):
            if event.kick_out:
                score += 0.1
        return min(1.0, score)

    if event.event_type == NarrationEventType.BALL_ADVANCE:
        return 0.3

    if event.event_type == NarrationEventType.OFF_BALL_ACTION:
        return 0.4

    if event.event_type == NarrationEventType.DEFENSIVE_ACTION:
        return 0.4

    return 0.3


class PossessionNarrator:
    """Composes full possession narratives from event streams.

    Collects events for a possession, then produces a multi-sentence
    narration combining play-by-play and color commentary. Uses
    importance scoring (no hard cap) and optionally the ChainComposer
    for flowing prose.
    """

    def __init__(
        self,
        pbp: PlayByPlayNarrator,
        color: ColorCommentaryNarrator,
        chain_composer: Optional["ChainComposer"] = None,
        pacing: Optional["PacingManager"] = None,
    ) -> None:
        self.pbp = pbp
        self.color = color
        self.chain_composer = chain_composer
        self.pacing = pacing
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

        Uses importance scoring to decide which events to narrate.
        If a ChainComposer is attached, setup events are composed into
        flowing prose instead of isolated sentences.
        """
        narration = PossessionNarration()

        # Score and filter events by importance
        significant = self._filter_significant_events()

        # Determine verbosity from pacing manager
        verbosity = 0.5
        if self.pacing:
            verbosity = self.pacing.score_verbosity(
                self._current_events,
                arc_snapshot,
            )

        # If we have a chain composer, use it for setup events
        if self.chain_composer:
            setup_events = [
                e for e in significant
                if e.event_type in _SETUP_TYPES
            ]
            terminal_events = [
                e for e in significant
                if e.event_type not in _SETUP_TYPES
            ]

            # Compose setup events into flowing prose
            if setup_events:
                composed = self.chain_composer.compose(
                    setup_events, verbosity=verbosity,
                )
                if composed:
                    narration.add_pbp(composed)

            # Terminal events still rendered individually
            for event in terminal_events:
                pbp_text = self.pbp.narrate(event)
                narration.add_pbp(pbp_text or "")

                if self.color.should_interject(event):
                    color_text = self.color.generate(event, arc_snapshot)
                    narration.add_color(color_text or "")
        else:
            # Fallback: render each event individually (original behavior)
            for event in significant:
                pbp_text = self.pbp.narrate(event)
                narration.add_pbp(pbp_text or "")

                if self.color.should_interject(event):
                    color_text = self.color.generate(event, arc_snapshot)
                    narration.add_color(color_text or "")

        return narration

    def _filter_significant_events(self) -> List[BaseNarrationEvent]:
        """Filter events using importance scoring instead of hard caps.

        All events above the importance threshold (0.3) are kept.
        Ball advance events are suppressed when better setup events exist.
        """
        if not self._current_events:
            return []

        scored = [
            (event, _compute_importance(event))
            for event in self._current_events
        ]

        # Keep everything above threshold
        threshold = 0.3
        kept = [event for event, score in scored if score > threshold]

        # Suppress ball advance if there are other setup events
        has_other_setup = any(
            e.event_type in _SETUP_TYPES and e.event_type != NarrationEventType.BALL_ADVANCE
            for e in kept
        )
        if has_other_setup:
            kept = [
                e for e in kept
                if e.event_type != NarrationEventType.BALL_ADVANCE
            ]

        return kept

    def compose_dead_ball(self, events: List[BaseNarrationEvent]) -> PossessionNarration:
        """Compose narration for dead ball events (between possessions)."""
        narration = PossessionNarration()
        for event in events:
            pbp_text = self.pbp.narrate(event)
            narration.add_pbp(pbp_text or "")
        return narration


# Setup event types used for chain composition grouping
_SETUP_TYPES = {
    NarrationEventType.DRIBBLE_MOVE,
    NarrationEventType.SCREEN_ACTION,
    NarrationEventType.PASS_ACTION,
    NarrationEventType.DRIVE,
    NarrationEventType.BALL_ADVANCE,
    NarrationEventType.OFF_BALL_ACTION,
    NarrationEventType.DEFENSIVE_ACTION,
}
