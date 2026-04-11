"""Broadcast mixer: interleaves play-by-play and color commentary.

Controls the ratio of PBP to color commentary (~70/30),
manages cooldowns, integrates pacing-aware verbosity, supports
broadcast segments (quarter intros, halftime, wrap), and produces
the final broadcast output.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING

from hoops_sim.narration.events import BaseNarrationEvent
from hoops_sim.narration.narrative_arc import ArcSnapshot, NarrativeArcTracker
from hoops_sim.narration.possession_narrator import (
    PossessionNarration,
    PossessionNarrator,
)
from hoops_sim.narration.stat_tracker import LiveStatTracker

if TYPE_CHECKING:
    from hoops_sim.narration.segments import BroadcastSegments
    from hoops_sim.narration.clock_narrator import ClockNarrator
    from hoops_sim.narration.game_memory import GameMemory


class VerbosityLevel(enum.Enum):
    """Output verbosity modes."""

    FULL_BROADCAST = "full_broadcast"
    HIGHLIGHTS_ONLY = "highlights_only"
    BOX_SCORE_SUMMARY = "box_score_summary"
    RADIO_MODE = "radio_mode"


@dataclass
class BroadcastLine:
    """A single line of broadcast output."""

    text: str
    voice: str = "pbp"  # "pbp" or "color"
    quarter: int = 1
    game_clock: float = 720.0
    home_score: int = 0
    away_score: int = 0
    intensity: float = 0.5  # 0.0 to 1.0


class BroadcastMixer:
    """Mixes play-by-play and color commentary into broadcast output.

    Manages pacing and ratio of PBP to color commentary. Supports
    optional broadcast segments (quarter intros, halftime, wrap) and
    clock-aware narration injection.
    """

    def __init__(
        self,
        possession_narrator: PossessionNarrator,
        stat_tracker: LiveStatTracker,
        arc_tracker: NarrativeArcTracker,
        verbosity: VerbosityLevel = VerbosityLevel.FULL_BROADCAST,
        segments: Optional["BroadcastSegments"] = None,
        clock_narrator: Optional["ClockNarrator"] = None,
        game_memory: Optional["GameMemory"] = None,
    ) -> None:
        self.narrator = possession_narrator
        self.stats = stat_tracker
        self.arcs = arc_tracker
        self.verbosity = verbosity
        self.segments = segments
        self.clock_narrator = clock_narrator
        self.game_memory = game_memory
        self._output: List[BroadcastLine] = []
        self._possession_count = 0
        self._current_quarter = 1
        self._current_clock = 720.0
        self._last_quarter_intro = 0

    def start_possession(
        self, quarter: int, game_clock: float,
    ) -> None:
        """Signal the start of a new possession."""
        self._possession_count += 1
        self._current_quarter = quarter
        self._current_clock = game_clock
        self.narrator.start_possession()

        # Emit quarter intro on quarter change
        if quarter != self._last_quarter_intro and quarter > 1:
            self._last_quarter_intro = quarter
            self._emit_quarter_intro(quarter)

    def add_event(self, event: BaseNarrationEvent) -> None:
        """Add a narration event to the current possession."""
        self.narrator.add_event(event)

    def end_possession(self) -> List[BroadcastLine]:
        """End the current possession and produce broadcast lines."""
        arc_snapshot = self.arcs.update(self._current_quarter, self._current_clock)
        narration = self.narrator.compose(arc_snapshot)

        # Inject clock context if available
        if self.clock_narrator:
            score_diff = self.stats.home_score - self.stats.away_score
            clock_phrase = self.clock_narrator.game_clock_phrase(
                self._current_quarter, self._current_clock, score_diff,
            )
            if clock_phrase and narration.pbp_lines:
                # Prepend clock context to the first PBP line
                narration.pbp_lines[0] = (
                    f"{clock_phrase} {narration.pbp_lines[0]}"
                )

        return self._emit_narration(narration, arc_snapshot)

    def emit_dead_ball(
        self, events: List[BaseNarrationEvent],
    ) -> List[BroadcastLine]:
        """Emit narration for dead ball events."""
        narration = self.narrator.compose_dead_ball(events)
        arc_snapshot = self.arcs.update(self._current_quarter, self._current_clock)
        return self._emit_narration(narration, arc_snapshot)

    def emit_halftime(self) -> List[BroadcastLine]:
        """Emit a halftime report segment."""
        if not self.segments:
            return []

        arc_snapshot = self.arcs.update(2, 0.0)
        text = self.segments.halftime_report(arc_snapshot)
        line = BroadcastLine(
            text=text,
            voice="color",
            quarter=2,
            game_clock=0.0,
            home_score=self.stats.home_score,
            away_score=self.stats.away_score,
            intensity=0.6,
        )
        self._output.append(line)
        return [line]

    def emit_game_end(self) -> List[BroadcastLine]:
        """Emit end-of-game wrap."""
        if not self.segments:
            return []

        arc_snapshot = self.arcs.update(self._current_quarter, 0.0)
        text = self.segments.end_of_game_wrap(arc_snapshot)
        line = BroadcastLine(
            text=text,
            voice="color",
            quarter=self._current_quarter,
            game_clock=0.0,
            home_score=self.stats.home_score,
            away_score=self.stats.away_score,
            intensity=0.7,
        )
        self._output.append(line)
        return [line]

    def _emit_quarter_intro(self, quarter: int) -> None:
        """Emit a quarter-start intro segment."""
        if not self.segments:
            return

        arc_snapshot = self.arcs.update(quarter, 720.0)
        text = self.segments.quarter_intro(quarter, arc_snapshot)
        line = BroadcastLine(
            text=text,
            voice="pbp",
            quarter=quarter,
            game_clock=720.0,
            home_score=self.stats.home_score,
            away_score=self.stats.away_score,
            intensity=0.5,
        )
        self._output.append(line)

    def _emit_narration(
        self, narration: PossessionNarration, arc_snapshot: ArcSnapshot,
    ) -> List[BroadcastLine]:
        """Convert a PossessionNarration into BroadcastLines."""
        lines: List[BroadcastLine] = []

        if not narration.has_content:
            return lines

        # Determine intensity from arc
        intensity = 0.5
        if arc_snapshot.has_active_arc and arc_snapshot.primary_arc:
            intensity = max(intensity, arc_snapshot.primary_arc.intensity)

        # Add PBP lines
        for text in narration.pbp_lines:
            if not text.strip():
                continue
            lines.append(BroadcastLine(
                text=text,
                voice="pbp",
                quarter=self._current_quarter,
                game_clock=self._current_clock,
                home_score=self.stats.home_score,
                away_score=self.stats.away_score,
                intensity=intensity,
            ))

        # Add color lines
        for text in narration.color_lines:
            if not text.strip():
                continue
            lines.append(BroadcastLine(
                text=text,
                voice="color",
                quarter=self._current_quarter,
                game_clock=self._current_clock,
                home_score=self.stats.home_score,
                away_score=self.stats.away_score,
                intensity=intensity,
            ))

        # Apply verbosity filter
        if self.verbosity == VerbosityLevel.HIGHLIGHTS_ONLY:
            lines = [l for l in lines if l.intensity >= 0.7]
        elif self.verbosity == VerbosityLevel.BOX_SCORE_SUMMARY:
            lines = []  # Box score mode doesn't emit per-possession

        self._output.extend(lines)
        return lines

    @property
    def all_output(self) -> List[BroadcastLine]:
        """All broadcast lines produced so far."""
        return self._output

    def score_header(self, home_team: str, away_team: str) -> str:
        """Produce a score header for the current game state."""
        q_str = f"Q{self._current_quarter}"
        minutes = int(self._current_clock // 60)
        seconds = int(self._current_clock % 60)
        clock_str = f"{minutes}:{seconds:02d}"
        return (
            f"=== {q_str} {clock_str} | "
            f"{home_team} {self.stats.home_score} - "
            f"{away_team} {self.stats.away_score} ==="
        )
