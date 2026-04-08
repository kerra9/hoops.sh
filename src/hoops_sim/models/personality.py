"""Player personality model.

Personality traits influence off-court behavior, team chemistry, media
interactions, and in-game emotional responses. These are distinct from
tendencies (which are gameplay-specific) and mental attributes (which
are skill-based).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlayerPersonality:
    """Personality traits that influence behavior on and off the court.

    All values range from 0.0 to 1.0.
    """

    # Core personality
    ego: float = 0.3  # Self-importance; high ego = demands touches, media attention
    competitiveness: float = 0.6  # Drive to win; affects rivalry intensity
    temperament: float = 0.6  # Emotional stability; low = volatile, high = calm
    sociability: float = 0.5  # Team bonding, locker room presence
    professionalism: float = 0.6  # Preparation, punctuality, media handling

    # Team dynamics
    alpha_mentality: float = 0.3  # Wants to be THE guy; multiple alphas = conflict
    loyalty: float = 0.5  # Preference for staying vs seeking new teams
    coachable: float = 0.6  # Acceptance of coaching decisions
    locker_room_presence: float = 0.5  # Impact on team morale (+/-)
    mentor_willing: float = 0.3  # Willingness to help young players

    # Media / public
    media_savvy: float = 0.5  # Handling of press, avoidance of controversy
    fan_friendly: float = 0.5  # Community engagement, fan interactions
    social_media_active: float = 0.4  # Social media presence (can cause drama)

    def is_high_ego(self) -> bool:
        """Check if player has problematic ego level."""
        return self.ego > 0.7

    def is_volatile(self) -> bool:
        """Check if player is emotionally volatile."""
        return self.temperament < 0.3

    def is_team_first(self) -> bool:
        """Check if player has a team-first mentality."""
        return self.ego < 0.4 and self.sociability > 0.5

    def chemistry_impact(self) -> float:
        """Estimate this player's impact on team chemistry.

        Positive = good locker room guy, Negative = potential problem.
        Returns roughly -1.0 to +1.0.
        """
        positive = (
            self.sociability * 0.25
            + self.professionalism * 0.20
            + self.locker_room_presence * 0.20
            + self.coachable * 0.15
            + self.temperament * 0.10
            + self.mentor_willing * 0.10
        )
        negative = self.ego * 0.5 + (1.0 - self.temperament) * 0.3 + self.social_media_active * 0.2
        return positive - negative * 0.5

    def tech_foul_tendency(self) -> float:
        """Likelihood of receiving a technical foul.

        Combines temperament, ego, and competitiveness.
        Returns 0.0 (saint) to ~0.3 (Rasheed Wallace).
        """
        return max(0.0, (
            (1.0 - self.temperament) * 0.4
            + self.ego * 0.3
            + self.competitiveness * 0.2
            - self.professionalism * 0.1
        ))
