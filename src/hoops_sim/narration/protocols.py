"""Protocol definitions for all seven pipeline layers.

Every layer boundary is defined by a Protocol. This means:
- Unit tests can mock any layer
- Alternative implementations can be swapped in
- The engine can be reconfigured without touching core code
"""

from __future__ import annotations

from typing import Protocol

from hoops_sim.narration.types import (
    Clause,
    DramaticPlan,
    EnrichedEvent,
    GameContext,
    GrammarClause,
    SequenceTag,
    StyledClause,
)
from hoops_sim.narration.events import BaseNarrationEvent
from hoops_sim.utils.rng import SeededRNG


class EventEnricher(Protocol):
    """Layer 1: Annotates raw events with narration-relevant context."""

    def enrich(
        self, event: BaseNarrationEvent, context: GameContext,
    ) -> EnrichedEvent: ...


class SequenceRecognizer(Protocol):
    """Layer 2: Identifies the type of basketball sequence."""

    def recognize(self, events: list[EnrichedEvent]) -> SequenceTag: ...


class Dramaturg(Protocol):
    """Layer 3: Plans the dramatic structure of the possession."""

    def plan(
        self,
        events: list[EnrichedEvent],
        sequence: SequenceTag,
        game_context: GameContext,
    ) -> DramaticPlan: ...


class ClauseGenerator(Protocol):
    """Layer 4: Converts dramatic beats into narrative clauses."""

    def generate(
        self, beat: "DramaticBeat", plan: DramaticPlan, rng: SeededRNG,
    ) -> list[Clause]: ...


class GrammarEngine(Protocol):
    """Layer 5: Transforms clauses into grammatically correct prose."""

    def process(
        self, clauses: list[Clause], plan: DramaticPlan,
    ) -> list[GrammarClause]: ...


class VoiceStyler(Protocol):
    """Layer 6: Injects announcer personality and style."""

    def style(
        self, clauses: list[GrammarClause], plan: DramaticPlan,
    ) -> list[StyledClause]: ...


class ProseRenderer(Protocol):
    """Layer 7: Joins styled clauses into the final output string."""

    def render(self, clauses: list[StyledClause]) -> str: ...
