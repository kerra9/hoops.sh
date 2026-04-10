"""Output formatting for different broadcast modes.

Supports: Full Broadcast, Highlights Only, Box Score Summary, Radio Mode.
"""

from __future__ import annotations

from typing import List

from hoops_sim.narration.broadcast_mixer import BroadcastLine, VerbosityLevel
from hoops_sim.narration.stat_tracker import LiveStatTracker


class BroadcastFormatter:
    """Formats broadcast output into different presentation modes."""

    def __init__(
        self,
        home_team: str,
        away_team: str,
        stat_tracker: LiveStatTracker,
        verbosity: VerbosityLevel = VerbosityLevel.FULL_BROADCAST,
    ) -> None:
        self.home_team = home_team
        self.away_team = away_team
        self.stats = stat_tracker
        self.verbosity = verbosity
        self._last_quarter = 0
        self._last_score_header = ""

    def format_lines(self, lines: List[BroadcastLine]) -> str:
        """Format a batch of broadcast lines into presentation text."""
        if not lines:
            return ""

        parts: List[str] = []

        for line in lines:
            # Insert quarter header on quarter change
            if line.quarter != self._last_quarter:
                self._last_quarter = line.quarter
                header = self._quarter_header(
                    line.quarter, line.game_clock,
                    line.home_score, line.away_score,
                )
                parts.append(f"\n{header}\n")

            # Format based on voice
            if self.verbosity == VerbosityLevel.FULL_BROADCAST:
                tag = "[PBP]" if line.voice == "pbp" else "[COLOR]"
                parts.append(f"{tag} {line.text}")
            elif self.verbosity == VerbosityLevel.RADIO_MODE:
                # Radio mode: more descriptive, no tags
                parts.append(line.text)
            else:
                parts.append(line.text)

        return "\n".join(parts)

    def format_score_update(self) -> str:
        """Format a current score update line."""
        return (
            f"{self.home_team} {self.stats.home_score}, "
            f"{self.away_team} {self.stats.away_score}"
        )

    def format_box_score_summary(self) -> str:
        """Format a condensed box score summary."""
        lines: List[str] = []
        lines.append(f"FINAL: {self.home_team} {self.stats.home_score}, "
                      f"{self.away_team} {self.stats.away_score}")
        lines.append("")

        # Top performers
        all_players = sorted(
            self.stats.players.values(),
            key=lambda p: p.points,
            reverse=True,
        )
        lines.append("TOP PERFORMERS:")
        for pstats in all_players[:5]:
            lines.append(f"  {pstats.player_name}: {pstats.stat_line()}")

        # Team stats
        lines.append("")
        lines.append("TEAM STATS:")
        for team_stats in [self.stats.home_stats, self.stats.away_stats]:
            fg_pct = f"{team_stats.fg_pct * 100:.1f}%"
            three_pct = f"{team_stats.three_pct * 100:.1f}%"
            lines.append(
                f"  {team_stats.team_name}: "
                f"FG {team_stats.fg_made}/{team_stats.fg_attempted} ({fg_pct}), "
                f"3PT {team_stats.three_made}/{team_stats.three_attempted} ({three_pct}), "
                f"TO {team_stats.turnovers}"
            )

        # Game info
        lines.append("")
        lines.append(f"Lead changes: {self.stats.lead_changes}")
        lines.append(f"Times tied: {self.stats.ties}")

        return "\n".join(lines)

    def _quarter_header(
        self, quarter: int, game_clock: float,
        home_score: int, away_score: int,
    ) -> str:
        """Generate a quarter header line."""
        quarter_names = {
            1: "1ST QUARTER", 2: "2ND QUARTER",
            3: "3RD QUARTER", 4: "4TH QUARTER",
        }
        q_name = quarter_names.get(quarter, f"OVERTIME {quarter - 4}")
        return (
            f"{'=' * 50}\n"
            f"  {q_name} | {self.home_team} {home_score} - "
            f"{self.away_team} {away_score}\n"
            f"{'=' * 50}"
        )
