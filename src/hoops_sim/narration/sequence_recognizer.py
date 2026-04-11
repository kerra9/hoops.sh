"""Layer 2: Sequence Recognition.

Identifies what *type of basketball sequence* the possession represents,
so the narration can follow the right dramatic template.

Recognized sequences: isolation, pick_and_roll, fast_break,
catch_and_shoot, post_up, drive_and_kick, off_ball, broken_play,
secondary_break.
"""

from __future__ import annotations

from hoops_sim.narration.events import (
    BallAdvanceEvent,
    DribbleMoveEvent,
    DriveEvent,
    NarrationEventType,
    PassEvent,
    ScreenEvent,
    ShotAttemptEvent,
    ShotClockPressureEvent,
    ShotResultEvent,
)
from hoops_sim.narration.types import EnrichedEvent, SequenceTag


class DefaultSequenceRecognizer:
    """Default implementation of the SequenceRecognizer protocol.

    Iterates through enriched events and pattern-matches against
    known basketball sequences. Returns the best match.
    """

    def recognize(self, events: list[EnrichedEvent]) -> SequenceTag:
        """Identify the primary sequence type from a list of enriched events."""
        if not events:
            return SequenceTag(primary="generic", confidence=0.3)

        raw_events = [e.raw for e in events]
        raw_types = [e.raw.event_type for e in events]

        # Check each sequence pattern
        tag = self._check_fast_break(events, raw_events, raw_types)
        if tag:
            return tag

        tag = self._check_pick_and_roll(events, raw_events, raw_types)
        if tag:
            return tag

        tag = self._check_catch_and_shoot(events, raw_events, raw_types)
        if tag:
            return tag

        tag = self._check_drive_and_kick(events, raw_events, raw_types)
        if tag:
            return tag

        tag = self._check_broken_play(events, raw_events, raw_types)
        if tag:
            return tag

        tag = self._check_isolation(events, raw_events, raw_types)
        if tag:
            return tag

        # Fallback: generic half-court set
        handler, defender = self._find_key_matchup(events)
        return SequenceTag(
            primary="generic",
            confidence=0.4,
            key_matchup=(handler, defender) if handler else None,
            complexity=self._compute_complexity(raw_types),
            tempo="medium",
        )

    # ------------------------------------------------------------------
    # Sequence detectors
    # ------------------------------------------------------------------

    def _check_fast_break(
        self,
        events: list[EnrichedEvent],
        raw_events: list,
        raw_types: list,
    ) -> SequenceTag | None:
        """Detect fast break: transition flag, short duration, few passes."""
        for raw in raw_events:
            if isinstance(raw, BallAdvanceEvent) and raw.is_transition:
                pass_count = sum(
                    1 for t in raw_types
                    if t == NarrationEventType.PASS_ACTION
                )
                if pass_count <= 1:
                    handler, defender = self._find_key_matchup(events)
                    return SequenceTag(
                        primary="fast_break",
                        confidence=0.85,
                        key_matchup=(handler, defender) if handler else None,
                        complexity=0.2,
                        tempo="fast",
                    )
        return None

    def _check_pick_and_roll(
        self,
        events: list[EnrichedEvent],
        raw_events: list,
        raw_types: list,
    ) -> SequenceTag | None:
        """Detect PnR: screen event followed by drive or pop."""
        has_screen = NarrationEventType.SCREEN_ACTION in raw_types
        has_drive = NarrationEventType.DRIVE in raw_types
        has_shot = any(
            t in raw_types
            for t in (NarrationEventType.SHOT_ATTEMPT, NarrationEventType.SHOT_RESULT)
        )

        if has_screen and (has_drive or has_shot):
            # Check if there's a kick-out (drive_and_kick variant)
            secondary = None
            for raw in raw_events:
                if isinstance(raw, PassEvent) and raw.is_kick_out:
                    secondary = "drive_and_kick"
                    break

            handler, defender = self._find_key_matchup(events)
            return SequenceTag(
                primary="pick_and_roll",
                confidence=0.8,
                secondary=secondary,
                key_matchup=(handler, defender) if handler else None,
                complexity=0.6,
                tempo="medium",
            )
        return None

    def _check_catch_and_shoot(
        self,
        events: list[EnrichedEvent],
        raw_events: list,
        raw_types: list,
    ) -> SequenceTag | None:
        """Detect catch-and-shoot: pass -> immediate shot, no dribble."""
        dribble_count = sum(
            1 for t in raw_types if t == NarrationEventType.DRIBBLE_MOVE
        )
        has_pass = NarrationEventType.PASS_ACTION in raw_types
        has_shot = any(
            t in raw_types
            for t in (NarrationEventType.SHOT_ATTEMPT, NarrationEventType.SHOT_RESULT)
        )

        if has_pass and has_shot and dribble_count == 0:
            # Check if the shot was catch-and-shoot
            for raw in raw_events:
                if isinstance(raw, ShotAttemptEvent) and raw.is_catch_and_shoot:
                    handler, defender = self._find_key_matchup(events)
                    return SequenceTag(
                        primary="catch_and_shoot",
                        confidence=0.85,
                        key_matchup=(handler, defender) if handler else None,
                        complexity=0.2,
                        tempo="fast",
                    )
            # Even without the flag, pass->shot with no dribbles is C&S
            if has_pass and has_shot and dribble_count == 0:
                handler, defender = self._find_key_matchup(events)
                return SequenceTag(
                    primary="catch_and_shoot",
                    confidence=0.6,
                    key_matchup=(handler, defender) if handler else None,
                    complexity=0.2,
                    tempo="fast",
                )
        return None

    def _check_drive_and_kick(
        self,
        events: list[EnrichedEvent],
        raw_events: list,
        raw_types: list,
    ) -> SequenceTag | None:
        """Detect drive-and-kick: drive + kick-out pass + perimeter shot."""
        has_drive = NarrationEventType.DRIVE in raw_types
        has_kick = any(
            isinstance(r, PassEvent) and r.is_kick_out for r in raw_events
        )
        has_shot = any(
            t in raw_types
            for t in (NarrationEventType.SHOT_ATTEMPT, NarrationEventType.SHOT_RESULT)
        )

        if has_drive and has_kick and has_shot:
            handler, defender = self._find_key_matchup(events)
            return SequenceTag(
                primary="drive_and_kick",
                confidence=0.8,
                key_matchup=(handler, defender) if handler else None,
                complexity=0.5,
                tempo="medium",
            )
        return None

    def _check_broken_play(
        self,
        events: list[EnrichedEvent],
        raw_events: list,
        raw_types: list,
    ) -> SequenceTag | None:
        """Detect broken play: shot clock pressure or desperation shot."""
        has_pressure = NarrationEventType.SHOT_CLOCK_PRESSURE in raw_types
        late_shot_clock = any(e.raw.shot_clock <= 5.0 for e in events if e.raw.shot_clock > 0)

        if has_pressure or late_shot_clock:
            handler, defender = self._find_key_matchup(events)
            return SequenceTag(
                primary="broken_play",
                confidence=0.75,
                key_matchup=(handler, defender) if handler else None,
                complexity=0.3,
                tempo="frantic",
            )
        return None

    def _check_isolation(
        self,
        events: list[EnrichedEvent],
        raw_events: list,
        raw_types: list,
    ) -> SequenceTag | None:
        """Detect isolation: single handler, 2+ dribble moves, no screen."""
        dribble_count = sum(
            1 for t in raw_types if t == NarrationEventType.DRIBBLE_MOVE
        )
        has_screen = NarrationEventType.SCREEN_ACTION in raw_types
        pass_count = sum(
            1 for t in raw_types if t == NarrationEventType.PASS_ACTION
        )

        if dribble_count >= 2 and not has_screen and pass_count <= 1:
            handler, defender = self._find_key_matchup(events)
            return SequenceTag(
                primary="isolation",
                confidence=0.75,
                key_matchup=(handler, defender) if handler else None,
                complexity=0.4 + (dribble_count * 0.1),
                tempo="slow",
            )
        return None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _find_key_matchup(
        events: list[EnrichedEvent],
    ) -> tuple[str, str]:
        """Find the primary handler/defender matchup."""
        handler = ""
        defender = ""
        for e in events:
            if e.player_name and not handler:
                handler = e.player_name
            if e.defender_name and not defender:
                defender = e.defender_name
            if handler and defender:
                break
        return handler, defender

    @staticmethod
    def _compute_complexity(raw_types: list) -> float:
        """Compute sequence complexity from event count/variety."""
        unique = len(set(raw_types))
        total = len(raw_types)
        return min(1.0, (unique * 0.15) + (total * 0.05))
