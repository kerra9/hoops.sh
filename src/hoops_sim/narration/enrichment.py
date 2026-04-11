"""Layer 1: Event Enrichment.

Annotates raw sim events with narration-relevant context that the
sim itself does not compute. This is the *only* place that touches
the player model, stat tracker, game memory, and spatial describer.
Everything downstream works with EnrichedEvent only.
"""

from __future__ import annotations

from hoops_sim.narration.events import (
    BaseNarrationEvent,
    BallAdvanceEvent,
    BlockEvent,
    DribbleMoveEvent,
    DriveEvent,
    FoulEvent,
    FreeThrowEvent,
    NarrationEventType,
    PassEvent,
    ReboundEvent,
    ScreenEvent,
    ShotAttemptEvent,
    ShotResultEvent,
    TurnoverEvent,
)
from hoops_sim.narration.types import EnrichedEvent, GameContext


class DefaultEventEnricher:
    """Default implementation of the EventEnricher protocol.

    Pulls context from the event's own fields and the GameContext
    to populate an EnrichedEvent. When player models, stat trackers,
    and game memory are available on the GameContext they are used;
    otherwise sensible defaults are returned.
    """

    def enrich(
        self, event: BaseNarrationEvent, context: GameContext,
    ) -> EnrichedEvent:
        """Enrich a single event with narration context."""
        player_name, player_id = self._extract_player(event)
        defender_name, defender_id = self._extract_defender(event)

        spatial = self._build_spatial(event)
        clock_ctx = self._build_clock_context(event, context)
        stat_ctx = self._build_stat_context(event)

        # Crowd energy rises with closeness of game and late-game clock
        crowd_energy = self._compute_crowd_energy(context)

        # Detect signature moves (ankle breakers, poster dunks, etc.)
        is_signature = self._detect_signature(event)

        return EnrichedEvent(
            raw=event,
            player_name=player_name,
            player_id=player_id,
            defender_name=defender_name,
            defender_id=defender_id,
            spatial=spatial,
            clock_context=clock_ctx,
            stat_context=stat_ctx,
            memory_callback=None,
            crowd_energy=crowd_energy,
            fatigue_level=0.0,
            emotion="neutral",
            is_signature_move=is_signature,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_player(event: BaseNarrationEvent) -> tuple[str, int]:
        """Pull the primary player name/id from any event type."""
        if isinstance(event, BallAdvanceEvent):
            return event.ball_handler_name, 0
        if isinstance(event, DribbleMoveEvent):
            return event.player_name, event.player_id
        if isinstance(event, DriveEvent):
            return event.driver_name, event.driver_id
        if isinstance(event, PassEvent):
            return event.passer_name, event.passer_id
        if isinstance(event, ShotAttemptEvent):
            return event.shooter_name, event.shooter_id
        if isinstance(event, ShotResultEvent):
            return event.shooter_name, event.shooter_id
        if isinstance(event, ScreenEvent):
            return event.handler_name, 0
        if isinstance(event, BlockEvent):
            return event.blocker_name, event.blocker_id
        if isinstance(event, ReboundEvent):
            return event.rebounder_name, event.rebounder_id
        if isinstance(event, TurnoverEvent):
            return event.player_name, event.player_id
        if isinstance(event, FoulEvent):
            return event.victim_name, event.victim_id
        if isinstance(event, FreeThrowEvent):
            return event.shooter_name, event.shooter_id
        # Fallback -- use generic attribute probing
        name = getattr(event, "player_name", "") or getattr(
            event, "ball_handler_name", ""
        )
        pid = getattr(event, "player_id", 0)
        return name, pid

    @staticmethod
    def _extract_defender(event: BaseNarrationEvent) -> tuple[str, int]:
        """Pull defender info from events that carry it."""
        if isinstance(event, DribbleMoveEvent):
            return event.defender_name, 0
        if isinstance(event, DriveEvent):
            return event.defender_name, 0
        if isinstance(event, ShotAttemptEvent):
            return event.defender_name, 0
        if isinstance(event, BlockEvent):
            return event.shooter_name, event.shooter_id
        return "", 0

    @staticmethod
    def _build_spatial(event: BaseNarrationEvent) -> str:
        """Build a spatial description from event fields."""
        if event.court_location:
            return event.court_location
        zone = getattr(event, "zone", "")
        if zone:
            from hoops_sim.narration.spatial import SpatialDescriber
            return SpatialDescriber.describe_location(zone)
        return ""

    @staticmethod
    def _build_clock_context(
        event: BaseNarrationEvent, context: GameContext,
    ) -> str | None:
        """Build clock urgency context if warranted."""
        # Late-game, close score situations
        if context.quarter >= 4 and context.game_clock <= 120.0:
            diff = abs(context.home_score - context.away_score)
            if diff <= 5:
                minutes = int(context.game_clock // 60)
                seconds = int(context.game_clock % 60)
                return f"{minutes}:{seconds:02d} remaining, {diff}-point game"
        # Shot clock pressure
        if event.shot_clock <= 5.0:
            return f"{event.shot_clock:.0f} on the shot clock"
        return None

    @staticmethod
    def _build_stat_context(event: BaseNarrationEvent) -> str | None:
        """Build stat context (e.g. 'his 4th three of the night')."""
        # This would ideally query LiveStatTracker but we keep it
        # simple for now -- enrichment does not depend on external state
        # beyond the event itself.
        return None

    @staticmethod
    def _compute_crowd_energy(context: GameContext) -> float:
        """Compute crowd energy from game state."""
        energy = 0.5
        diff = abs(context.home_score - context.away_score)
        # Close games are exciting
        if diff <= 5:
            energy += 0.2
        elif diff <= 10:
            energy += 0.1
        # Late game is more exciting
        if context.quarter >= 4:
            energy += 0.15
            if context.game_clock <= 120.0:
                energy += 0.15
        return min(1.0, energy)

    @staticmethod
    def _detect_signature(event: BaseNarrationEvent) -> bool:
        """Detect if this event is a signature/highlight move."""
        if isinstance(event, DribbleMoveEvent):
            return event.ankle_breaker
        if isinstance(event, ShotResultEvent):
            return event.is_dunk or event.is_and_one
        return False
