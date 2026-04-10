"""Free agency: players sign with teams based on money, role, and market.

After the draft, free agents choose teams based on salary offers,
projected role, market size, and existing relationships.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.models.player import Player
from hoops_sim.utils.rng import SeededRNG


@dataclass
class FreeAgent:
    """A player available in free agency."""

    player: Player
    asking_salary: int = 5_000_000  # What the player wants
    years_wanted: int = 2
    priority: str = "money"  # "money", "winning", "role", "location"


@dataclass
class ContractOffer:
    """A contract offer from a team to a free agent."""

    team_id: int
    team_name: str
    player_id: int
    salary: int
    years: int
    role: str = "bench"  # "star", "starter", "rotation", "bench"
    team_wins_last_season: int = 0
    market_size: str = "medium"  # "large", "medium", "small"


@dataclass
class SigningResult:
    """Result of a free agent signing."""

    player: Player
    team_id: int
    team_name: str
    salary: int
    years: int


def evaluate_offer(
    agent: FreeAgent,
    offer: ContractOffer,
    rng: SeededRNG,
) -> float:
    """Score a contract offer for a free agent.

    Higher score = more attractive to the player.

    Args:
        agent: The free agent.
        offer: The contract offer.
        rng: Random number generator.

    Returns:
        Attractiveness score (0-100).
    """
    score = 50.0

    # Money factor
    salary_ratio = offer.salary / max(agent.asking_salary, 1)
    score += min(salary_ratio * 15, 25)  # Up to +25 for overpay

    # Role factor
    role_values = {"star": 20, "starter": 15, "rotation": 8, "bench": 2}
    score += role_values.get(offer.role, 5)

    # Winning factor
    if offer.team_wins_last_season >= 50:
        score += 10
    elif offer.team_wins_last_season >= 40:
        score += 5

    # Market size
    market_values = {"large": 5, "medium": 2, "small": 0}
    score += market_values.get(offer.market_size, 0)

    # Years factor (longer = more security)
    if offer.years >= agent.years_wanted:
        score += 5

    # Priority alignment
    if agent.priority == "money" and salary_ratio > 1.0:
        score += 10
    elif agent.priority == "winning" and offer.team_wins_last_season >= 50:
        score += 15
    elif agent.priority == "role" and offer.role in ("star", "starter"):
        score += 12

    # Random noise for unpredictability
    score += rng.gauss(0, 5)

    return max(0, min(100, score))


def run_free_agency(
    free_agents: list[FreeAgent],
    team_offers: dict[int, list[ContractOffer]],
    rng: SeededRNG,
) -> list[SigningResult]:
    """Process free agency: each agent picks their best offer.

    Args:
        free_agents: List of available free agents.
        team_offers: Map of player_id to list of offers.
        rng: Random number generator.

    Returns:
        List of signings.
    """
    signings: list[SigningResult] = []

    for agent in free_agents:
        offers = team_offers.get(agent.player.id, [])
        if not offers:
            continue

        # Evaluate each offer
        scored = [(evaluate_offer(agent, o, rng), o) for o in offers]
        scored.sort(key=lambda x: x[0], reverse=True)

        # Player signs with the best offer
        best_score, best_offer = scored[0]
        if best_score > 30:  # Minimum threshold
            signings.append(SigningResult(
                player=agent.player,
                team_id=best_offer.team_id,
                team_name=best_offer.team_name,
                salary=best_offer.salary,
                years=best_offer.years,
            ))

    return signings
