"""NBA Draft: lottery, draft order, and rookie generation.

Handles the draft lottery for non-playoff teams, generates draft prospects
with scouting reports, and executes the two-round draft.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from hoops_sim.data.generator import generate_player
from hoops_sim.models.player import Player
from hoops_sim.utils.rng import SeededRNG


@dataclass
class DraftProspect:
    """A draft-eligible prospect with scouting info."""

    player: Player
    projected_pick: int = 0
    scout_grade: str = ""  # "A+", "A", "B+", etc.
    comparison: str = ""  # "Reminds scouts of..."
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)


@dataclass
class DraftPick:
    """A single draft pick."""

    pick_number: int
    round: int
    team_id: int
    team_name: str
    player: Player | None = None


@dataclass
class DraftResult:
    """Complete result of a draft."""

    season_year: int
    picks: list[DraftPick] = field(default_factory=list)
    prospects: list[DraftProspect] = field(default_factory=list)


# Scout grade thresholds
GRADE_THRESHOLDS = [
    (85, "A+"), (80, "A"), (75, "A-"), (70, "B+"), (65, "B"),
    (60, "B-"), (55, "C+"), (50, "C"), (45, "C-"), (0, "D"),
]

# Comparison player archetypes for fun scouting reports
COMPARISONS = [
    "a young LeBron James", "Kobe Bryant", "Stephen Curry",
    "Tim Duncan", "Kevin Durant", "Chris Paul", "Giannis Antetokounmpo",
    "Kawhi Leonard", "Luka Doncic", "Jayson Tatum", "Nikola Jokic",
    "Anthony Edwards", "Ja Morant", "Damian Lillard", "Joel Embiid",
]

STRENGTHS_POOL = [
    "elite scorer", "excellent passer", "lockdown defender",
    "athletic freak", "high basketball IQ", "great shooter",
    "strong rebounder", "clutch performer", "natural leader",
    "motor never stops", "versatile on both ends", "elite handles",
]

WEAKNESSES_POOL = [
    "inconsistent jumper", "needs to add strength", "turnover prone",
    "defensive awareness", "shot selection", "free throw shooting",
    "lateral quickness", "conditioning", "low motor at times",
    "limited range", "foul trouble", "ball security",
]


def generate_draft_class(
    rng: SeededRNG,
    num_prospects: int = 60,
) -> list[DraftProspect]:
    """Generate a draft class of prospects.

    Top picks are higher rated, later picks are lower rated.

    Args:
        rng: Random number generator.
        num_prospects: Number of prospects to generate.

    Returns:
        List of DraftProspect sorted by projected pick.
    """
    prospects: list[DraftProspect] = []

    for i in range(num_prospects):
        # Overall target decreases with pick number
        if i < 5:
            target = rng.randint(72, 80)
            age = rng.randint(19, 21)
        elif i < 14:
            target = rng.randint(65, 75)
            age = rng.randint(19, 22)
        elif i < 30:
            target = rng.randint(58, 68)
            age = rng.randint(20, 23)
        else:
            target = rng.randint(50, 62)
            age = rng.randint(21, 24)

        player = generate_player(rng, overall_target=target, age=age)
        player.years_pro = 0  # Rookie

        # Scout grade
        grade = "D"
        for threshold, g in GRADE_THRESHOLDS:
            if player.overall >= threshold:
                grade = g
                break

        prospect = DraftProspect(
            player=player,
            projected_pick=i + 1,
            scout_grade=grade,
            comparison=rng.choice(COMPARISONS),
            strengths=rng.choices(STRENGTHS_POOL, k=min(3, len(STRENGTHS_POOL))),
            weaknesses=rng.choices(WEAKNESSES_POOL, k=min(2, len(WEAKNESSES_POOL))),
        )
        prospects.append(prospect)

    return prospects


def determine_draft_order(
    team_records: list[tuple[int, str, int, int]],
    playoff_team_ids: set[int],
    rng: SeededRNG,
) -> list[tuple[int, str]]:
    """Determine draft order using a simplified lottery.

    Non-playoff teams get lottery picks (1-14), weighted by inverse record.
    Playoff teams pick 15-30 in reverse order of elimination.

    Args:
        team_records: List of (team_id, team_name, wins, losses).
        playoff_team_ids: Set of team IDs that made the playoffs.
        rng: Random number generator.

    Returns:
        List of (team_id, team_name) in draft order.
    """
    lottery_teams = [
        (tid, name, w, l) for tid, name, w, l in team_records
        if tid not in playoff_team_ids
    ]
    playoff_teams = [
        (tid, name, w, l) for tid, name, w, l in team_records
        if tid in playoff_team_ids
    ]

    # Lottery: worse teams get more ping-pong balls
    # Sort by wins ascending (worst first)
    lottery_teams.sort(key=lambda x: x[2])

    # Simplified lottery: top 4 picks are randomized among bottom 4 teams
    # remaining lottery teams fill 5-14 in order
    lottery_order: list[tuple[int, str]] = []
    if len(lottery_teams) >= 4:
        bottom_4 = list(lottery_teams[:4])
        rng.shuffle(bottom_4)
        for tid, name, _, _ in bottom_4:
            lottery_order.append((tid, name))
        for tid, name, _, _ in lottery_teams[4:]:
            lottery_order.append((tid, name))
    else:
        for tid, name, _, _ in lottery_teams:
            lottery_order.append((tid, name))

    # Playoff teams pick in reverse order of wins
    playoff_teams.sort(key=lambda x: x[2])
    playoff_order = [(tid, name) for tid, name, _, _ in playoff_teams]

    # Two rounds
    first_round = lottery_order + playoff_order
    second_round = list(first_round)  # Same order for round 2

    return first_round + second_round


def execute_draft(
    draft_order: list[tuple[int, str]],
    prospects: list[DraftProspect],
    season_year: int = 2025,
) -> DraftResult:
    """Execute the draft: each team picks the best available prospect.

    Args:
        draft_order: List of (team_id, team_name) in pick order.
        prospects: Available prospects sorted by projected pick.
        season_year: The season year.

    Returns:
        DraftResult with all picks.
    """
    result = DraftResult(season_year=season_year, prospects=list(prospects))
    available = list(prospects)

    for i, (team_id, team_name) in enumerate(draft_order):
        if not available:
            break

        round_num = 1 if i < len(draft_order) // 2 else 2
        pick = DraftPick(
            pick_number=i + 1,
            round=round_num,
            team_id=team_id,
            team_name=team_name,
        )

        # Simple AI: pick the highest-rated available player
        best = max(available, key=lambda p: p.player.overall)
        pick.player = best.player
        available.remove(best)

        result.picks.append(pick)

    return result
