"""Intermediate data types for the seven-layer narration pipeline.

All data types that flow between pipeline layers are defined here.
Each type is a plain dataclass. No layer knows about the internals
of another -- they communicate solely through these types.

Data flow:
    SimEvent[] -> EnrichedEvent[] -> SequenceTag -> DramaticPlan
    -> Clause[] -> GrammarClause[] -> StyledClause[] -> str
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional

from hoops_sim.narration.events import BaseNarrationEvent


# ---------------------------------------------------------------------------
# Layer 1 output: EnrichedEvent
# ---------------------------------------------------------------------------


@dataclass
class EnrichedEvent:
    """A narration event annotated with all narration-relevant context.

    Produced by Layer 1 (Event Enrichment). This is the *only* type
    that downstream layers work with -- they never touch the player
    model, stat tracker, or game memory directly.
    """

    raw: BaseNarrationEvent
    player_name: str = ""
    player_id: int = 0
    defender_name: str = ""
    defender_id: int = 0
    spatial: str = ""
    clock_context: Optional[str] = None
    stat_context: Optional[str] = None
    memory_callback: Optional[str] = None
    crowd_energy: float = 0.5
    fatigue_level: float = 0.0
    emotion: str = "neutral"
    is_signature_move: bool = False


# ---------------------------------------------------------------------------
# Layer 2 output: SequenceTag
# ---------------------------------------------------------------------------


@dataclass
class SequenceTag:
    """Identifies what type of basketball sequence the possession represents.

    Produced by Layer 2 (Sequence Recognition).
    """

    primary: str = "generic"  # "isolation", "pick_and_roll", etc.
    confidence: float = 0.5
    secondary: Optional[str] = None
    key_matchup: Optional[tuple[str, str]] = None  # (handler, defender)
    complexity: float = 0.3
    tempo: str = "medium"  # "slow", "medium", "fast", "frantic"


# ---------------------------------------------------------------------------
# Layer 3 output: DramaticPlan
# ---------------------------------------------------------------------------


class DramaticRole(enum.Enum):
    """The dramatic role of an event within a possession's story arc."""

    ESTABLISH = "establish"  # Setting the scene
    BUILD = "build"  # Rising action
    PIVOT = "pivot"  # The moment it changes
    CLIMAX = "climax"  # The payoff
    AFTERMATH = "aftermath"  # Reaction
    ASIDE = "aside"  # Color commentary insertion


@dataclass
class DramaticBeat:
    """A single event with its dramatic role and intensity assigned.

    Produced by Layer 3 (Possession Dramaturgy).
    """

    event: EnrichedEvent
    role: DramaticRole
    intensity: float = 0.3  # 0.0-1.0
    defender_dignity: float = 1.0  # 1.0 = composed, 0.0 = on the floor
    is_turning_point: bool = False


@dataclass
class DramaticPlan:
    """The complete dramatic plan for a possession.

    Produced by Layer 3 (Possession Dramaturgy).
    """

    beats: list[DramaticBeat] = field(default_factory=list)
    sequence: SequenceTag = field(default_factory=SequenceTag)
    peak_intensity: float = 0.5
    curve_shape: str = "linear"  # "exponential", "linear", "spike", "flat"
    crowd_moment: Optional[int] = None  # beat index where crowd reacts


# ---------------------------------------------------------------------------
# Layer 4 output: Clause
# ---------------------------------------------------------------------------


@dataclass
class Clause:
    """The atomic unit of prose -- a single narrative clause.

    Produced by Layer 4 (Clause Generation).
    """

    text: str
    subject: Optional[str] = None
    subject_type: str = "handler"  # "handler", "defender", "announcer", "crowd"
    intensity: float = 0.3
    role: DramaticRole = DramaticRole.BUILD
    is_defender_clause: bool = False
    is_reaction: bool = False
    is_signature: bool = False
    source_event_type: str = ""
    tags: set[str] = field(default_factory=set)


# ---------------------------------------------------------------------------
# Layer 5 output: GrammarClause
# ---------------------------------------------------------------------------


@dataclass
class GrammarClause:
    """A clause with grammar decisions applied.

    Produced by Layer 5 (Grammar Engine).
    """

    text: str
    connector: str = ""  # how to join to previous clause
    capitalization: str = "normal"  # "normal", "sentence", "upper"
    terminal_punctuation: str = ""  # "", ".", "!", "..."


# ---------------------------------------------------------------------------
# Layer 6 output: StyledClause
# ---------------------------------------------------------------------------


@dataclass
class StyledClause:
    """A clause with voice/style applied.

    Produced by Layer 6 (Voice and Style).
    """

    text: str
    connector: str = ""
    is_caps: bool = False
    terminal: str = ""
    voice: str = "pbp"  # "pbp" or "color"
    is_catchphrase: bool = False


# ---------------------------------------------------------------------------
# Cross-cutting: GameContext
# ---------------------------------------------------------------------------


@dataclass
class GameContext:
    """All context the narration pipeline needs, gathered once per possession.

    Constructed by the BroadcastMixer at the start of each possession
    and threaded through all layers. No layer reaches out to global state.
    """

    quarter: int = 1
    game_clock: float = 720.0
    shot_clock: float = 24.0
    home_score: int = 0
    away_score: int = 0
    home_team: str = ""
    away_team: str = ""
    possession_number: int = 0
