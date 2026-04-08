"""Pairwise player relationship model.

Every pair of teammates has a relationship that affects on-court chemistry,
passing accuracy, screen quality, and help defense responsiveness.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple


@dataclass
class Relationship:
    """A relationship between two players.

    Attributes:
        affinity: How much they like each other (-100 to +100).
        trust: On-court trust built through positive interactions (0-100).
        rivalry: Competitive tension (0-100). Not always bad -- can motivate.
    """

    affinity: int = 0
    trust: int = 50
    rivalry: int = 0

    def clamp(self) -> None:
        """Clamp all values to valid ranges."""
        self.affinity = max(-100, min(100, self.affinity))
        self.trust = max(0, min(100, self.trust))
        self.rivalry = max(0, min(100, self.rivalry))

    def on_court_passing_mod(self) -> float:
        """How this relationship affects passing accuracy between these two.

        Returns: modifier from -0.10 to +0.10.
        """
        return self.affinity * 0.001

    def on_court_screen_mod(self) -> float:
        """How this relationship affects screen quality.

        Players who trust each other set better screens.
        Returns: modifier from 0.0 to +0.10.
        """
        return self.trust * 0.001

    def on_court_help_defense_mod(self) -> float:
        """How this relationship affects help defense responsiveness.

        Higher trust = faster and more reliable help defense.
        Returns: modifier from 0.0 to +0.08.
        """
        return self.trust * 0.0008

    def is_positive(self) -> bool:
        """Whether the overall relationship is positive."""
        return self.affinity > 0

    def is_strong_bond(self) -> bool:
        """Whether the players have a strong positive bond."""
        return self.affinity > 50 and self.trust > 70

    def is_toxic(self) -> bool:
        """Whether the relationship is actively harmful."""
        return self.affinity < -50


@dataclass
class RelationshipMatrix:
    """Pairwise relationships between all players on a team.

    Uses player IDs as keys. Only stores relationships for relevant pairs
    (teammates, frequent opponents). Untracked pairs use neutral defaults.
    """

    relationships: Dict[Tuple[int, int], Relationship] = field(default_factory=dict)

    def _key(self, player_a: int, player_b: int) -> Tuple[int, int]:
        """Canonical key for a player pair (always sorted)."""
        return (min(player_a, player_b), max(player_a, player_b))

    def get(self, player_a: int, player_b: int) -> Relationship:
        """Get the relationship between two players.

        Returns a neutral relationship if none is tracked.
        """
        key = self._key(player_a, player_b)
        if key not in self.relationships:
            self.relationships[key] = Relationship()
        return self.relationships[key]

    def set(self, player_a: int, player_b: int, relationship: Relationship) -> None:
        """Set the relationship between two players."""
        key = self._key(player_a, player_b)
        self.relationships[key] = relationship

    def modify_affinity(self, player_a: int, player_b: int, delta: int) -> None:
        """Adjust affinity between two players."""
        rel = self.get(player_a, player_b)
        rel.affinity += delta
        rel.clamp()

    def modify_trust(self, player_a: int, player_b: int, delta: int) -> None:
        """Adjust trust between two players."""
        rel = self.get(player_a, player_b)
        rel.trust += delta
        rel.clamp()

    def all_relationships_for(self, player_id: int) -> Dict[int, Relationship]:
        """Get all relationships involving a specific player."""
        result: Dict[int, Relationship] = {}
        for (a, b), rel in self.relationships.items():
            if a == player_id:
                result[b] = rel
            elif b == player_id:
                result[a] = rel
        return result

    def team_chemistry_score(self) -> float:
        """Calculate overall team chemistry from all pairwise relationships.

        Returns: score from -100 to +100, where 0 is neutral.
        """
        if not self.relationships:
            return 0.0
        total_affinity = sum(r.affinity for r in self.relationships.values())
        total_trust = sum(r.trust for r in self.relationships.values())
        count = len(self.relationships)
        avg_affinity = total_affinity / count
        avg_trust = total_trust / count
        return avg_affinity * 0.6 + (avg_trust - 50) * 0.4
