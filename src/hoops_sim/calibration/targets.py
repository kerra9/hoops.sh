"""NBA statistical calibration targets.

Defines the target ranges for key statistics that the simulation
should produce. Used by the calibration harness to evaluate whether
the engine is producing realistic results.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CalibrationTarget:
    """A single calibration target with acceptable range."""

    name: str
    nba_average: float
    min_acceptable: float
    max_acceptable: float
    unit: str = ""

    def is_in_range(self, value: float) -> bool:
        return self.min_acceptable <= value <= self.max_acceptable

    def deviation(self, value: float) -> float:
        """How far off the value is from the NBA average, as a fraction."""
        if self.nba_average == 0:
            return 0.0
        return abs(value - self.nba_average) / self.nba_average


# Per-team per-game targets
TEAM_TARGETS = [
    CalibrationTarget("points_per_game", 110.0, 95.0, 125.0, "pts"),
    CalibrationTarget("fg_pct", 0.47, 0.44, 0.50, "%"),
    CalibrationTarget("three_pct", 0.36, 0.33, 0.39, "%"),
    CalibrationTarget("three_attempts", 35.0, 30.0, 42.0, "att"),
    CalibrationTarget("ft_pct", 0.78, 0.75, 0.81, "%"),
    CalibrationTarget("ft_attempts", 22.0, 18.0, 27.0, "att"),
    CalibrationTarget("turnovers", 14.0, 11.0, 17.0, "to"),
    CalibrationTarget("assists", 25.0, 22.0, 28.0, "ast"),
    CalibrationTarget("rebounds", 44.0, 40.0, 48.0, "reb"),
    CalibrationTarget("steals", 7.5, 6.0, 10.0, "stl"),
    CalibrationTarget("blocks", 5.0, 3.5, 6.5, "blk"),
    CalibrationTarget("possessions", 100.0, 95.0, 105.0, "poss"),
    CalibrationTarget("avg_possession_length", 14.0, 12.0, 16.0, "sec"),
    CalibrationTarget("fast_break_points", 14.0, 10.0, 18.0, "pts"),
    CalibrationTarget("points_in_paint", 50.0, 44.0, 56.0, "pts"),
]

# Per-player calibration for elite players
ELITE_PLAYER_TARGETS = [
    CalibrationTarget("elite_ppg", 28.0, 25.0, 35.0, "pts"),
    CalibrationTarget("elite_fg_pct", 0.48, 0.44, 0.52, "%"),
    CalibrationTarget("elite_apg", 6.0, 4.0, 8.0, "ast"),
]

ELITE_SHOOTER_TARGETS = [
    CalibrationTarget("elite_3pt_pct", 0.40, 0.38, 0.44, "%"),
    CalibrationTarget("elite_3pt_attempts", 8.0, 6.0, 11.0, "att"),
]


@dataclass
class CalibrationReport:
    """Report from a calibration run."""

    games_simulated: int = 0
    targets_met: int = 0
    targets_total: int = 0
    results: list[tuple[str, float, bool]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.results is None:
            self.results = []

    @property
    def pass_rate(self) -> float:
        if self.targets_total == 0:
            return 0.0
        return self.targets_met / self.targets_total

    def add_result(self, name: str, value: float, target: CalibrationTarget) -> None:
        in_range = target.is_in_range(value)
        self.results.append((name, value, in_range))
        self.targets_total += 1
        if in_range:
            self.targets_met += 1

    def summary(self) -> str:
        lines = [f"Calibration: {self.targets_met}/{self.targets_total} targets met "
                 f"({self.pass_rate:.0%}) over {self.games_simulated} games"]
        for name, value, passed in self.results:
            status = "PASS" if passed else "FAIL"
            lines.append(f"  [{status}] {name}: {value:.2f}")
        return "\n".join(lines)
