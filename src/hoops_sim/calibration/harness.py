"""Calibration harness for running bulk simulations and checking stats.

Simulates many games and compares aggregate statistics against NBA
targets to verify the engine produces realistic results.
"""

from __future__ import annotations

from hoops_sim.calibration.targets import (
    TEAM_TARGETS,
    CalibrationReport,
)
from hoops_sim.data.generator import generate_roster
from hoops_sim.engine.simulator import GameSimulator
from hoops_sim.models.team import Team
from hoops_sim.utils.rng import SeededRNG


def run_calibration(
    num_games: int = 100,
    base_seed: int = 1000,
) -> CalibrationReport:
    """Run a calibration suite.

    Simulates num_games games with different seeds and checks the
    aggregate statistics against NBA targets.

    Args:
        num_games: Number of games to simulate.
        base_seed: Starting seed for RNG.

    Returns:
        CalibrationReport with results.
    """
    # Accumulators
    total_points: list[float] = []
    total_fga: list[float] = []
    total_fgm: list[float] = []
    total_3pa: list[float] = []
    total_3pm: list[float] = []
    total_fta: list[float] = []
    total_ftm: list[float] = []
    total_turnovers: list[float] = []
    total_assists: list[float] = []
    total_rebounds: list[float] = []
    total_steals: list[float] = []
    total_blocks: list[float] = []
    total_possessions: list[float] = []
    total_paint_pts: list[float] = []

    for i in range(num_games):
        seed = base_seed + i
        rng = SeededRNG(seed=seed)

        home = Team(
            id=1, city="Home", name="Team", abbreviation="HOM",
            conference="East", division="Atlantic",
            roster=generate_roster(rng),
        )
        away_rng = SeededRNG(seed=seed + 10000)
        away = Team(
            id=2, city="Away", name="Team", abbreviation="AWY",
            conference="West", division="Pacific",
            roster=generate_roster(away_rng),
        )

        sim = GameSimulator(home_team=home, away_team=away, seed=seed, narrate=False)
        result = sim.simulate_full_game()

        # Collect stats for both teams
        for stats, score in [
            (result.home_stats, result.home_score),
            (result.away_stats, result.away_score),
        ]:
            total_points.append(float(score))
            team_fga = sum(ps.fga for ps in stats.player_stats.values())
            team_fgm = sum(ps.fgm for ps in stats.player_stats.values())
            team_3pa = sum(ps.three_pa for ps in stats.player_stats.values())
            team_3pm = sum(ps.three_pm for ps in stats.player_stats.values())
            team_fta = sum(ps.fta for ps in stats.player_stats.values())
            team_ftm = sum(ps.ftm for ps in stats.player_stats.values())
            team_to = sum(ps.turnovers for ps in stats.player_stats.values())
            team_ast = sum(ps.assists for ps in stats.player_stats.values())
            team_reb = sum(
                ps.offensive_rebounds + ps.defensive_rebounds
                for ps in stats.player_stats.values()
            )
            team_stl = sum(ps.steals for ps in stats.player_stats.values())
            team_blk = sum(ps.blocks for ps in stats.player_stats.values())

            total_fga.append(float(team_fga))
            total_fgm.append(float(team_fgm))
            total_3pa.append(float(team_3pa))
            total_3pm.append(float(team_3pm))
            total_fta.append(float(team_fta))
            total_ftm.append(float(team_ftm))
            total_turnovers.append(float(team_to))
            total_assists.append(float(team_ast))
            total_rebounds.append(float(team_reb))
            total_steals.append(float(team_stl))
            total_blocks.append(float(team_blk))
            total_possessions.append(float(result.total_possessions))
            total_paint_pts.append(float(stats.points_in_paint))

    # Calculate averages
    n = len(total_points)

    def avg(lst: list[float]) -> float:
        return sum(lst) / max(1, len(lst))

    report = CalibrationReport(games_simulated=num_games)

    # Check each target
    stat_values = {
        "points_per_game": avg(total_points),
        "fg_pct": sum(total_fgm) / max(1, sum(total_fga)),
        "three_pct": sum(total_3pm) / max(1, sum(total_3pa)),
        "three_attempts": avg(total_3pa),
        "ft_pct": sum(total_ftm) / max(1, sum(total_fta)),
        "ft_attempts": avg(total_fta),
        "turnovers": avg(total_turnovers),
        "assists": avg(total_assists),
        "rebounds": avg(total_rebounds),
        "steals": avg(total_steals),
        "blocks": avg(total_blocks),
        "possessions": avg(total_possessions),
        "points_in_paint": avg(total_paint_pts),
    }

    for target in TEAM_TARGETS:
        if target.name in stat_values:
            report.add_result(target.name, stat_values[target.name], target)

    return report
