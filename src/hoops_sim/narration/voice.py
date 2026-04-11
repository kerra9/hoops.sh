"""Layer 6: Voice and Style.

Injects announcer personality -- catchphrases, signature reactions,
and broadcast style. Maps GrammarClauses to StyledClauses with
voice-specific modifications.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.narration.types import DramaticPlan, DramaticRole, GrammarClause, StyledClause
from hoops_sim.utils.rng import SeededRNG


@dataclass
class AnnouncerProfile:
    """Configuration for an announcer's voice and style."""

    name: str = "Classic"
    style: str = "balanced"  # "dramatic", "analytical", "poetic", "hype"

    # Catchphrase banks
    three_pointer_calls: list[str] = field(default_factory=lambda: [
        "BANG!", "FROM DOWNTOWN!", "SPLASH!", "Count it!",
    ])
    dunk_calls: list[str] = field(default_factory=lambda: [
        "THROWS IT DOWN!", "OH WHAT A MONSTER JAM!", "SLAM!",
    ])
    ankle_breaker_calls: list[str] = field(default_factory=lambda: [
        "BROKE HIS ANKLES!", "OH MY GOODNESS!", "FILTHY!",
    ])
    block_calls: list[str] = field(default_factory=lambda: [
        "GET THAT OUTTA HERE!", "REJECTED!", "NOT IN MY HOUSE!",
    ])
    general_reactions: list[str] = field(default_factory=lambda: [
        "MY GOODNESS!", "WHAT A PLAY!", "UNBELIEVABLE!", "ARE YOU KIDDING ME?!",
    ])
    staredown_phrases: list[str] = field(default_factory=lambda: [
        "STARES HIM DOWN", "LOOKS RIGHT AT HIM",
    ])
    separation_phrases: list[str] = field(default_factory=lambda: [
        "LOOK AT THIS SEPARATION!", "ALL ALONE!",
    ])
    crowd_references: list[str] = field(default_factory=lambda: [
        "the crowd is on its feet!", "listen to this building!",
    ])

    # Style parameters
    caps_threshold: float = 0.85
    exclamation_density: float = 0.5
    ellipsis_love: float = 0.4
    verbosity: float = 0.5
    defender_focus: float = 0.5
    crowd_awareness: float = 0.3

    # Rhythm preferences
    preferred_clause_length: str = "medium"
    sentence_rhythm: str = "mixed"


class DefaultVoiceStyler:
    """Default implementation of the VoiceStyler protocol.

    Applies announcer personality to grammar clauses, injecting
    catchphrases, adjusting capitalization, and setting voice tags.
    """

    def __init__(
        self,
        profile: AnnouncerProfile | None = None,
        rng: SeededRNG | None = None,
    ) -> None:
        self.profile = profile or AnnouncerProfile()
        self._rng = rng or SeededRNG(0)

    def style(
        self, clauses: list[GrammarClause], plan: DramaticPlan,
    ) -> list[StyledClause]:
        """Apply voice styling to grammar clauses."""
        styled: list[StyledClause] = []

        for gc in clauses:
            text = gc.text
            is_caps = gc.capitalization == "upper"
            terminal = gc.terminal_punctuation

            # Apply capitalization
            if gc.capitalization == "upper":
                text = text.upper()
            elif gc.capitalization == "sentence":
                text = text[0].upper() + text[1:] if text else text

            styled.append(StyledClause(
                text=text,
                connector=gc.connector,
                is_caps=is_caps,
                terminal=terminal,
                voice="pbp",
                is_catchphrase=False,
            ))

        # Inject crowd reference after climax if profile likes it
        if (
            plan.crowd_moment is not None
            and plan.peak_intensity >= 0.7
            and self._rng.random() < self.profile.crowd_awareness
        ):
            crowd_text = self._rng.choice(self.profile.crowd_references)
            styled.append(StyledClause(
                text=crowd_text,
                connector=" ",
                is_caps=False,
                terminal="",
                voice="color",
                is_catchphrase=False,
            ))

        return styled
