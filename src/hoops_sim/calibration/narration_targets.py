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

    def check_targets(self) -> List[str]:
        """Check calibration targets and return list of issues."""
        issues: List[str] = []

        # Words per possession: target 30-80
        wpp = self.words_per_possession
        if wpp < 15:
            issues.append(
                f"Words per possession too low: {wpp:.1f} (target: 30-80)"
            )
        elif wpp > 120:
            issues.append(
                f"Words per possession too high: {wpp:.1f} (target: 30-80)"
            )

        # Narration coverage: target > 90%
        cov = self.narration_coverage
        if cov < 0.8:
            issues.append(
                f"Narration coverage low: {cov:.1%} (target: >90%)"
            )

        # Color frequency: target 20-40% of possessions
        cf = self.color_frequency
        if cf < 0.1:
            issues.append(
                f"Color commentary too rare: {cf:.1%} (target: 20-40%)"
            )
        elif cf > 0.6:
            issues.append(
                f"Color commentary too frequent: {cf:.1%} (target: 20-40%)"
            )

        # Template diversity: no template > 5% of total uses
        total_uses = sum(self.template_uses.values()) if self.template_uses else 1
        for tmpl, count in self.template_uses.items():
            if count / total_uses > 0.10:
                issues.append(
                    f"Template overused ({count}/{total_uses}): {tmpl[:60]}..."
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
        ]
        issues = self.check_targets()
        if issues:
            lines.append("\nISSUES:")
            for issue in issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("\nAll targets met!")
        return "\n".join(lines)
