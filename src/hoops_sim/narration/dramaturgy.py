"""Layer 3: Possession Dramaturgy.

Plans the narrative structure of the possession. Assigns each event
a dramatic role and computes the intensity curve. This is the
creative brain of the engine -- it decides *what kind of story*
this possession tells and *how dramatically* to tell it.
"""

from __future__ import annotations

from hoops_sim.narration.events import (
    BallAdvanceEvent,
    BlockEvent,
    DribbleMoveEvent,
    DriveEvent,
    FoulEvent,
    FreeThrowEvent,
    MomentumEvent,
    NarrationEventType,
    PassEvent,
    ProbingEvent,
    ReboundEvent,
    ScreenEvent,
    ShotAttemptEvent,
    ShotResultEvent,
    TurnoverEvent,
)
from hoops_sim.narration.types import (
    DramaticBeat,
    DramaticPlan,
    DramaticRole,
    EnrichedEvent,
    GameContext,
    SequenceTag,
)


# Terminal event types that are always the CLIMAX
_TERMINAL_TYPES = {
    NarrationEventType.SHOT_RESULT,
    NarrationEventType.TURNOVER,
    NarrationEventType.BLOCK,
    NarrationEventType.FOUL,
}

# Aftermath event types
_AFTERMATH_TYPES = {
    NarrationEventType.REBOUND,
    NarrationEventType.FREE_THROW,
    NarrationEventType.MOMENTUM,
    NarrationEventType.MILESTONE,
    NarrationEventType.CROWD_REACTION,
}


class DefaultDramaturg:
    """Default implementation of the Dramaturg protocol.

    Assigns dramatic roles, computes intensity curves, and tracks
    defender dignity through the possession.
    """

    def plan(
        self,
        events: list[EnrichedEvent],
        sequence: SequenceTag,
        game_context: GameContext,
    ) -> DramaticPlan:
        """Build a dramatic plan for the possession."""
        if not events:
            return DramaticPlan(sequence=sequence)

        # Assign roles to each event
        roles = self._assign_roles(events)

        # Compute intensity curve
        base_curve = self._compute_base_curve(roles, sequence)

        # Apply intensity modifiers
        modifiers = self._compute_modifiers(events, sequence, game_context)
        final_intensities = [
            min(1.0, base * mod)
            for base, mod in zip(base_curve, modifiers)
        ]

        # Track defender dignity
        dignities = self._track_defender_dignity(events)

        # Find turning points
        turning_points = self._find_turning_points(events, roles)

        # Build beats
        beats: list[DramaticBeat] = []
        peak_intensity = 0.0
        crowd_moment = None

        for i, (ev, role, intensity, dignity) in enumerate(
            zip(events, roles, final_intensities, dignities)
        ):
            is_tp = i in turning_points
            beat = DramaticBeat(
                event=ev,
                role=role,
                intensity=intensity,
                defender_dignity=dignity,
                is_turning_point=is_tp,
            )
            beats.append(beat)
            if intensity > peak_intensity:
                peak_intensity = intensity

            # Crowd reacts at the first CLIMAX or very high intensity
            if crowd_moment is None and (
                role == DramaticRole.CLIMAX or intensity >= 0.85
            ):
                crowd_moment = i

        curve_shape = self._determine_curve_shape(sequence)

        return DramaticPlan(
            beats=beats,
            sequence=sequence,
            peak_intensity=peak_intensity,
            curve_shape=curve_shape,
            crowd_moment=crowd_moment,
        )

    # ------------------------------------------------------------------
    # Role assignment
    # ------------------------------------------------------------------

    def _assign_roles(
        self, events: list[EnrichedEvent],
    ) -> list[DramaticRole]:
        """Assign a dramatic role to each event."""
        roles: list[DramaticRole] = []
        climax_assigned = False

        for i, ev in enumerate(events):
            etype = ev.raw.event_type

            if etype in _AFTERMATH_TYPES:
                roles.append(DramaticRole.AFTERMATH)
                continue

            if etype in _TERMINAL_TYPES:
                roles.append(DramaticRole.CLIMAX)
                climax_assigned = True
                continue

            # If we already hit climax, everything after is aftermath
            if climax_assigned:
                roles.append(DramaticRole.AFTERMATH)
                continue

            # First event or ball advance is ESTABLISH
            if i == 0 or etype == NarrationEventType.BALL_ADVANCE:
                roles.append(DramaticRole.ESTABLISH)
                continue

            # Ankle breakers and big drives are PIVOT
            if isinstance(ev.raw, DribbleMoveEvent) and ev.raw.ankle_breaker:
                roles.append(DramaticRole.PIVOT)
                continue

            if etype == NarrationEventType.DRIVE:
                roles.append(DramaticRole.PIVOT)
                continue

            # Shot attempt just before result is PIVOT
            if etype == NarrationEventType.SHOT_ATTEMPT:
                roles.append(DramaticRole.PIVOT)
                continue

            # Everything else is BUILD
            roles.append(DramaticRole.BUILD)

        return roles

    # ------------------------------------------------------------------
    # Intensity curve
    # ------------------------------------------------------------------

    def _compute_base_curve(
        self,
        roles: list[DramaticRole],
        sequence: SequenceTag,
    ) -> list[float]:
        """Compute the base intensity curve from role positions."""
        n = len(roles)
        if n == 0:
            return []

        # Base values by role
        role_base = {
            DramaticRole.ESTABLISH: 0.15,
            DramaticRole.BUILD: 0.35,
            DramaticRole.PIVOT: 0.65,
            DramaticRole.CLIMAX: 0.85,
            DramaticRole.AFTERMATH: 0.6,
            DramaticRole.ASIDE: 0.2,
        }

        curve: list[float] = []
        for i, role in enumerate(roles):
            base = role_base.get(role, 0.3)
            # Position-based ramp: later events in BUILD phase get higher
            if role == DramaticRole.BUILD and n > 2:
                progress = i / (n - 1)
                base += progress * 0.2
            curve.append(min(1.0, base))

        return curve

    def _compute_modifiers(
        self,
        events: list[EnrichedEvent],
        sequence: SequenceTag,
        context: GameContext,
    ) -> list[float]:
        """Compute multiplicative intensity modifiers per event."""
        modifiers: list[float] = []

        for ev in events:
            mod = 1.0

            # Game clock: Q4 under 2 min, close game
            if context.quarter >= 4 and context.game_clock <= 120.0:
                diff = abs(context.home_score - context.away_score)
                if diff <= 5:
                    mod *= 1.4
                elif diff <= 10:
                    mod *= 1.2

            # Ankle breaker / poster dunk instant spike
            if isinstance(ev.raw, DribbleMoveEvent) and ev.raw.ankle_breaker:
                mod *= 1.5
            if isinstance(ev.raw, ShotResultEvent) and ev.raw.is_dunk:
                mod *= 1.3

            # Crowd energy
            mod *= 1.0 + (ev.crowd_energy - 0.5) * 0.4

            # Signature move
            if ev.is_signature_move:
                mod *= 1.1

            # Sequence tempo adjustments
            if sequence.tempo == "fast":
                mod *= 1.1
            elif sequence.tempo == "frantic":
                mod *= 1.2

            modifiers.append(mod)

        return modifiers

    # ------------------------------------------------------------------
    # Defender dignity
    # ------------------------------------------------------------------

    def _track_defender_dignity(
        self, events: list[EnrichedEvent],
    ) -> list[float]:
        """Track defender dignity through the possession."""
        dignity = 1.0
        dignities: list[float] = []

        for ev in events:
            raw = ev.raw
            if isinstance(raw, DribbleMoveEvent):
                if raw.ankle_breaker:
                    dignity = max(0.0, dignity - 0.5)
                elif raw.separation_gained > 0.3:
                    dignity = max(0.0, dignity - 0.2)
                elif raw.success:
                    dignity = max(0.0, dignity - 0.1)
            elif isinstance(raw, ScreenEvent):
                if raw.switch_occurred:
                    dignity = max(0.0, dignity - 0.1)
            elif isinstance(raw, DriveEvent):
                dignity = max(0.0, dignity - 0.15)

            dignities.append(dignity)

        return dignities

    # ------------------------------------------------------------------
    # Turning points and curve shape
    # ------------------------------------------------------------------

    def _find_turning_points(
        self,
        events: list[EnrichedEvent],
        roles: list[DramaticRole],
    ) -> set[int]:
        """Find indices where the narrative shifts."""
        turning = set()
        for i, (ev, role) in enumerate(zip(events, roles)):
            if role == DramaticRole.PIVOT:
                turning.add(i)
            if isinstance(ev.raw, DribbleMoveEvent) and ev.raw.ankle_breaker:
                turning.add(i)
        return turning

    @staticmethod
    def _determine_curve_shape(sequence: SequenceTag) -> str:
        """Determine the intensity curve shape based on sequence type."""
        shape_map = {
            "isolation": "exponential",
            "fast_break": "spike",
            "pick_and_roll": "linear",
            "catch_and_shoot": "spike",
            "broken_play": "exponential",
            "post_up": "linear",
            "drive_and_kick": "linear",
        }
        return shape_map.get(sequence.primary, "linear")
