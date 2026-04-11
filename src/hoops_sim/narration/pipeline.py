"""NarrationPipeline: orchestrates all seven layers.

This is the main entry point for the v2 narration engine. It chains
all seven layers in sequence and produces the final broadcast prose.

Data flow:
    SimEvent[] -> EnrichedEvent[] -> SequenceTag -> DramaticPlan
    -> Clause[] -> GrammarClause[] -> StyledClause[] -> str
"""

from __future__ import annotations

from hoops_sim.narration.anti_repetition import AntiRepetitionSystem, SentenceShape
from hoops_sim.narration.clause_gen import DefaultClauseGenerator
from hoops_sim.narration.dramaturgy import DefaultDramaturg
from hoops_sim.narration.enrichment import DefaultEventEnricher
from hoops_sim.narration.events import BaseNarrationEvent
from hoops_sim.narration.grammar import DefaultGrammarEngine
from hoops_sim.narration.prose_renderer import DefaultProseRenderer
from hoops_sim.narration.sequence_recognizer import DefaultSequenceRecognizer
from hoops_sim.narration.types import (
    Clause,
    DramaticPlan,
    EnrichedEvent,
    GameContext,
    GrammarClause,
    SequenceTag,
    StyledClause,
)
from hoops_sim.narration.voice import AnnouncerProfile, DefaultVoiceStyler
from hoops_sim.utils.rng import SeededRNG


class NarrationPipeline:
    """Orchestrates the seven-layer narration pipeline.

    Each layer is independently configurable and swappable.
    The pipeline produces a single string for each possession.
    """

    def __init__(
        self,
        rng: SeededRNG | None = None,
        announcer_profile: AnnouncerProfile | None = None,
    ) -> None:
        self._rng = rng or SeededRNG(42)

        # Layer implementations (all swappable)
        self.enricher = DefaultEventEnricher()
        self.recognizer = DefaultSequenceRecognizer()
        self.dramaturg = DefaultDramaturg()
        self.clause_generator = DefaultClauseGenerator()
        self.grammar_engine = DefaultGrammarEngine(rng=self._rng)
        self.voice_styler = DefaultVoiceStyler(
            profile=announcer_profile, rng=self._rng,
        )
        self.prose_renderer = DefaultProseRenderer()

        # Cross-cutting systems
        self.anti_repetition = AntiRepetitionSystem()

    def narrate(
        self,
        events: list[BaseNarrationEvent],
        context: GameContext | None = None,
    ) -> str:
        """Run the full seven-layer pipeline on a possession's events.

        Args:
            events: Raw narration events from the simulation.
            context: Game context for this possession. If None, a
                default context is constructed.

        Returns:
            A single string of broadcast-quality prose.
        """
        if not events:
            return ""

        ctx = context or GameContext()

        # Layer 1: Event Enrichment
        enriched: list[EnrichedEvent] = [
            self.enricher.enrich(e, ctx) for e in events
        ]

        # Layer 2: Sequence Recognition
        sequence: SequenceTag = self.recognizer.recognize(enriched)

        # Layer 3: Possession Dramaturgy
        plan: DramaticPlan = self.dramaturg.plan(enriched, sequence, ctx)

        # Layer 4: Clause Generation
        all_clauses: list[Clause] = []
        for beat in plan.beats:
            clauses = self.clause_generator.generate(beat, plan, self._rng)
            all_clauses.extend(clauses)

        if not all_clauses:
            return ""

        # Layer 5: Grammar Engine
        grammar_clauses: list[GrammarClause] = self.grammar_engine.process(
            all_clauses, plan,
        )

        # Layer 6: Voice and Style
        styled_clauses: list[StyledClause] = self.voice_styler.style(
            grammar_clauses, plan,
        )

        # Layer 7: Prose Rendering
        output: str = self.prose_renderer.render(styled_clauses)

        # Record anti-repetition data
        clause_texts = [c.text for c in all_clauses]
        word_count = len(output.split())
        themes = self._extract_themes(all_clauses)

        # Build sentence shape for structure tracking
        connector_pattern = "-".join(
            gc.connector.strip() or "none" for gc in grammar_clauses[:5]
        )
        climax_pos = 0.0
        for i, c in enumerate(all_clauses):
            if c.role.value == "climax":
                climax_pos = i / max(1, len(all_clauses) - 1)
                break

        shape = SentenceShape(
            clause_count=len(all_clauses),
            connector_pattern=connector_pattern,
            climax_position=climax_pos,
        )
        self.anti_repetition.record_possession(
            clause_texts, word_count, shape, themes,
        )

        return output

    @staticmethod
    def _extract_themes(clauses: list[Clause]) -> list[str]:
        """Extract narrative themes used in this possession."""
        themes: list[str] = []
        for c in clauses:
            if "ankle_breaker" in c.tags:
                themes.append("ankle_breaker")
            if "staredown" in c.tags:
                themes.append("staredown")
            if "defender" in c.tags and c.is_defender_clause:
                themes.append("defender_humiliation")
            if "reaction" in c.tags and "crowd" in c.text.lower():
                themes.append("crowd_going_wild")
        return list(set(themes))
