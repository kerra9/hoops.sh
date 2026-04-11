"""Narration quality calibration targets.

Defines measurable quality targets for narration output:
- Words per possession
- Template repetition rate
- Color commentary frequency
- Statistical reference frequency
- Dead ball narration coverage
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class NarrationCalibrationResult:
    """Result of running narration calibration checks."""

    total_possessions: int = 0
    total_words: int = 0
    total_pbp_lines: int = 0
    total_color_lines: int = 0
    possessions_with_narration: int = 0
    possessions_with_color: int = 0
    template_uses: Dict[str, int] = field(default_factory=dict)
    score_references: int = 0
    timeouts_narrated: int = 0
    timeouts_total: int = 0
    substitutions_narrated: int = 0
    substitutions_total: int = 0

    @property
    def words_per_possession(self) -> float:
        if self.total_possessions == 0:
            return 0.0
        return self.total_words / self.total_possessions

    @property
    def narration_coverage(self) -> float:
        if self.total_possessions == 0:
            return 0.0
        return self.possessions_with_narration / self.total_possessions

    @property
    def color_frequency(self) -> float:
        """Color commentary lines per possession."""
        if self.total_possessions == 0:
            return 0.0
        return self.possessions_with_color / self.total_possessions

    @property
    def max_template_repetition(self) -> int:
        """Most times any single template was used."""
        if not self.template_uses:
            return 0
        return max(self.template_uses.values())

    @property
    def unique_templates_used(self) -> int:
        return len(self.template_uses)

    # Extended metrics for the broadcast-quality narration system
    spatial_references: int = 0
    clock_references: int = 0
    callback_references: int = 0
    dribble_combo_chains: int = 0
    half_court_possessions: int = 0

    @property
    def spatial_reference_rate(self) -> float:
        """Fraction of possessions with spatial location references."""
        if self.total_possessions == 0:
            return 0.0
        return self.spatial_references / self.total_possessions

    @property
    def clock_reference_rate_q4(self) -> float:
        """Clock reference rate in Q4 (approximate)."""
        # Approximation: Q4 is ~25% of possessions
        q4_possessions = max(1, self.total_possessions // 4)
        return self.clock_references / q4_possessions

    def check_targets(self) -> List[str]:
        """Check calibration targets and return list of issues."""
        issues: List[str] = []

        # Words per possession: target 25-120 (variable by pacing)
        wpp = self.words_per_possession
        if wpp < 15:
            issues.append(
                f"Words per possession too low: {wpp:.1f} (target: 25-120)"
            )
        elif wpp > 150:
            issues.append(
                f"Words per possession too high: {wpp:.1f} (target: 25-120)"
            )

        # Narration coverage: target > 98%
        cov = self.narration_coverage
        if cov < 0.90:
            issues.append(
                f"Narration coverage low: {cov:.1%} (target: >98%)"
            )

        # Color frequency: target 30-50% of possessions
        cf = self.color_frequency
        if cf < 0.1:
            issues.append(
                f"Color commentary too rare: {cf:.1%} (target: 30-50%)"
            )
        elif cf > 0.7:
            issues.append(
                f"Color commentary too frequent: {cf:.1%} (target: 30-50%)"
            )

        # Template diversity: no template > 3% of total uses
        total_uses = sum(self.template_uses.values()) if self.template_uses else 1
        for tmpl, count in self.template_uses.items():
            if count / total_uses > 0.10:
                issues.append(
                    f"Template overused ({count}/{total_uses}): {tmpl[:60]}..."
                )

        # Spatial references: target >60% of possessions
        if self.spatial_references > 0 and self.spatial_reference_rate < 0.3:
            issues.append(
                f"Spatial references low: {self.spatial_reference_rate:.1%} "
                f"(target: >60%)"
            )

        # Callback references: target 5-15 per game
        if self.callback_references > 0 and self.callback_references < 3:
            issues.append(
                f"Callback references low: {self.callback_references} "
                f"(target: 5-15 per game)"
            )

        return issues

    def summary(self) -> str:
        """Human-readable calibration summary."""
        lines = [
            "=== Narration Calibration Report ===",
            f"Possessions: {self.total_possessions}",
            f"Words per possession: {self.words_per_possession:.1f}",
            f"Narration coverage: {self.narration_coverage:.1%}",
            f"Color commentary frequency: {self.color_frequency:.1%}",
            f"PBP lines: {self.total_pbp_lines}",
            f"Color lines: {self.total_color_lines}",
            f"Unique templates used: {self.unique_templates_used}",
            f"Max template repetition: {self.max_template_repetition}",
            f"Spatial references: {self.spatial_references}",
            f"Clock references: {self.clock_references}",
            f"Callback references: {self.callback_references}",
            f"Dribble combo chains: {self.dribble_combo_chains}",
        ]
        issues = self.check_targets()
        if issues:
            lines.append("\nISSUES:")
            for issue in issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("\nAll targets met!")
        return "\n".join(lines)
