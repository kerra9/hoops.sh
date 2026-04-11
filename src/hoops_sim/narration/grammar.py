"""Layer 5: Grammar Engine.

Transforms raw clauses into grammatically correct, flowing English
with proper subject management, connector selection, and tense
consistency. This is what separates a real narration engine from
'join strings with ellipses.'
"""

from __future__ import annotations

from hoops_sim.narration.clause_banks.connector import get_connectors
from hoops_sim.narration.types import Clause, DramaticPlan, DramaticRole, GrammarClause
from hoops_sim.utils.rng import SeededRNG


class SubjectTracker:
    """Tracks the current narrative subject for elision decisions.

    Rules:
    1. First mention: Full name. 'Harden brings the ball up'
    2. Continued action by same subject: Elide. 'jab step, sizes up Holiday'
    3. Subject switch: Restate. 'Holiday struggles to keep up'
    4. Subject switch back: Last name only. 'Harden with the snatchback'
    5. High intensity about same subject: CAPS LAST NAME.
    6. Defender as subject at high intensity: CAPS.
    """

    def __init__(self) -> None:
        self.current_subject: str | None = None
        self.mention_count: int = 0
        self._seen: set[str] = set()

    def resolve(self, clause: Clause) -> str:
        """Decide how to render the subject for this clause."""
        if clause.subject is None:
            return ""  # announcer reaction, no subject needed

        if clause.subject == self.current_subject:
            self.mention_count += 1
            if self.mention_count <= 2:
                return ""  # elide: "jab step" not "Harden jab step"
            return ""  # still elide for same subject

        # Subject switch
        prev = self.current_subject
        self.current_subject = clause.subject
        self.mention_count = 0

        # High intensity: CAPS
        if clause.intensity >= 0.85:
            self._seen.add(clause.subject)
            return clause.subject.upper()

        # Previously seen subject: use as-is (last name context)
        if clause.subject in self._seen:
            return clause.subject

        self._seen.add(clause.subject)
        return clause.subject


class DefaultGrammarEngine:
    """Default implementation of the GrammarEngine protocol."""

    def __init__(self, rng: SeededRNG | None = None) -> None:
        self._rng = rng or SeededRNG(0)

    def process(
        self, clauses: list[Clause], plan: DramaticPlan,
    ) -> list[GrammarClause]:
        """Transform clauses into grammatically correct grammar clauses."""
        if not clauses:
            return []

        tracker = SubjectTracker()
        result: list[GrammarClause] = []

        for i, clause in enumerate(clauses):
            subject = tracker.resolve(clause)

            # Build text with resolved subject
            if subject:
                text = f"{subject} {clause.text}"
            else:
                text = clause.text

            # Determine connector
            if i == 0:
                connector = ""
            else:
                prev = clauses[i - 1]
                connector = self._select_connector(prev, clause)

            # Determine capitalization
            cap = self._determine_capitalization(clause, i)

            # Determine terminal punctuation
            terminal = self._determine_terminal(clause, i, len(clauses))

            result.append(GrammarClause(
                text=text,
                connector=connector,
                capitalization=cap,
                terminal_punctuation=terminal,
            ))

        return result

    def _select_connector(self, prev: Clause, curr: Clause) -> str:
        """Select the connector between two clauses."""
        from_role = prev.role.value
        to_role = curr.role.value

        # Determine intensity trend
        if curr.intensity > prev.intensity + 0.1:
            trend = "rising"
        elif curr.intensity < prev.intensity - 0.1:
            trend = "falling"
        else:
            trend = "flat"

        options = get_connectors(from_role, to_role, trend)
        return self._rng.choice(options) if options else ", "

    @staticmethod
    def _determine_capitalization(clause: Clause, index: int) -> str:
        """Determine capitalization mode for a clause."""
        if clause.intensity >= 0.85:
            return "upper"
        if index == 0 or clause.is_reaction:
            return "sentence"
        return "normal"

    @staticmethod
    def _determine_terminal(clause: Clause, index: int, total: int) -> str:
        """Determine terminal punctuation for a clause."""
        # Reactions get exclamation
        if clause.is_reaction:
            return "!"
        # CLIMAX gets exclamation
        if clause.role == DramaticRole.CLIMAX:
            return "!"
        # Last clause gets period
        if index == total - 1:
            return "."
        # Otherwise no terminal (connector handles joining)
        return ""
