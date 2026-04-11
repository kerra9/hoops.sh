"""Cross-cutting: Anti-Repetition System.

Ensures no two possessions in a game sound the same. Operates at
four independent levels: vocabulary, structure, rhythm, and thematic.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


class VocabularyTracker:
    """Level 1: Clause-level deduplication.

    Tracks recently used clause texts and rejects clauses that
    have been used in the last N possessions.
    """

    def __init__(self, window: int = 15) -> None:
        self._recent: deque[str] = deque(maxlen=window)

    def is_fresh(self, text: str) -> bool:
        """Check if a clause text hasn't been used recently."""
        normalized = text.lower().strip()
        return normalized not in self._recent

    def record(self, text: str) -> None:
        """Record a clause text as recently used."""
        self._recent.append(text.lower().strip())

    def filter_fresh(self, options: list[str]) -> list[str]:
        """Filter a list of clause options to only fresh ones."""
        fresh = [t for t in options if self.is_fresh(t)]
        return fresh if fresh else options  # fallback to all if none fresh


@dataclass
class SentenceShape:
    """Level 2: Sentence structure fingerprint."""

    clause_count: int = 0
    connector_pattern: str = ""  # e.g. "comma-ellipsis-bang"
    climax_position: float = 0.0  # 0.0-1.0, where the climax hit


class StructureTracker:
    """Level 2: Sentence-level structure deduplication.

    Tracks the shape of recent sentences and flags when too many
    consecutive possessions have the same structure.
    """

    def __init__(self, window: int = 5) -> None:
        self._recent: deque[SentenceShape] = deque(maxlen=window)

    def record(self, shape: SentenceShape) -> None:
        """Record a sentence shape."""
        self._recent.append(shape)

    def is_repetitive(self, shape: SentenceShape) -> bool:
        """Check if this shape matches the last N shapes."""
        if len(self._recent) < 3:
            return False
        recent = list(self._recent)[-3:]
        return all(
            s.clause_count == shape.clause_count
            and s.connector_pattern == shape.connector_pattern
            for s in recent
        )


class RhythmTracker:
    """Level 3: Tempo-level variation tracking.

    Enforces word count variation across possessions:
    - After 2 long possessions, next routine play should be short
    - After 3 short possessions, allow next interesting play to breathe
    """

    def __init__(self, window: int = 5) -> None:
        self._word_counts: deque[int] = deque(maxlen=window)

    def record(self, word_count: int) -> None:
        """Record a possession's word count."""
        self._word_counts.append(word_count)

    def suggest_length(self) -> str:
        """Suggest whether next possession should be short, medium, or long."""
        if len(self._word_counts) < 2:
            return "medium"

        recent = list(self._word_counts)
        last_two = recent[-2:]

        # After 2 long possessions, go short
        if all(wc > 50 for wc in last_two):
            return "short"

        # After 3 short possessions, allow long
        if len(recent) >= 3 and all(wc < 20 for wc in recent[-3:]):
            return "long"

        return "medium"


class ThematicTracker:
    """Level 4: Narrative theme cooldown tracking.

    Spaces out recurring narrative themes so the broadcast doesn't
    hammer the same notes repeatedly.
    """

    def __init__(self) -> None:
        self._theme_cooldowns: dict[str, int] = {}
        self._default_cooldowns: dict[str, int] = {
            "defender_humiliation": 5,
            "crowd_going_wild": 4,
            "signature_move_call": 8,
            "scoring_run_reference": 3,
            "staredown": 6,
            "ankle_breaker": 5,
        }

    def can_use(self, theme: str) -> bool:
        """Check if a theme is off cooldown."""
        return self._theme_cooldowns.get(theme, 0) <= 0

    def record_use(self, theme: str) -> None:
        """Put a theme on cooldown."""
        cooldown = self._default_cooldowns.get(theme, 3)
        self._theme_cooldowns[theme] = cooldown

    def tick(self) -> None:
        """Advance all cooldowns by one possession."""
        for theme in list(self._theme_cooldowns):
            self._theme_cooldowns[theme] = max(
                0, self._theme_cooldowns[theme] - 1,
            )


class AntiRepetitionSystem:
    """Combined anti-repetition system with all four levels."""

    def __init__(self) -> None:
        self.vocabulary = VocabularyTracker()
        self.structure = StructureTracker()
        self.rhythm = RhythmTracker()
        self.thematic = ThematicTracker()

    def tick(self) -> None:
        """Advance all cooldowns after a possession."""
        self.thematic.tick()

    def record_possession(
        self,
        clause_texts: list[str],
        word_count: int,
        shape: SentenceShape | None = None,
        themes: list[str] | None = None,
    ) -> None:
        """Record all anti-repetition data for a completed possession."""
        for text in clause_texts:
            self.vocabulary.record(text)
        self.rhythm.record(word_count)
        if shape:
            self.structure.record(shape)
        for theme in (themes or []):
            self.thematic.record_use(theme)
        self.tick()
