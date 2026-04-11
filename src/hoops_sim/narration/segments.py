"""Broadcast segments beyond live play -- quarter intros, halftime, wrap.

Real broadcasts have structure: pre-game teasers, quarter-start context,
halftime analysis, and post-game summaries. These frame the game as a
story with narrative arcs.
"""

from __future__ import annotations

from typing import List, Optional

from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.narration.narrative_arc import ArcSnapshot, NarrativeArcTracker
from hoops_sim.utils.rng import SeededRNG


class BroadcastSegments:
    """Generates structural broadcast segments.

    Quarter intros, halftime reports, and end-of-game wraps.
    """

    def __init__(
        self,
        rng: SeededRNG,
        stat_tracker: LiveStatTracker,
        home_team: str,
        away_team: str,
    ) -> None:
        self.rng = rng
        self.stats = stat_tracker
        self.home_team = home_team
        self.away_team = away_team

    def quarter_intro(self, quarter: int, arc_snapshot: ArcSnapshot) -> str:
        """Generate a quarter-start teaser.

        At the start of Q2, Q3, Q4: score, key storyline, what to watch.
        """
        score_line = self._score_line()

        if quarter == 2:
            lead_team, margin = self._lead_info()
            storyline = self._top_performer_line()
            return (
                f"Back to action. {score_line} "
                f"{storyline}"
            )

        if quarter == 3:
            storyline = self._top_performer_line()
            return (
                f"Second half underway. {score_line} "
                f"{storyline}"
            )

        if quarter == 4:
            lead_team, margin = self._lead_info()
            if margin <= 5:
                return (
                    f"Fourth quarter. {score_line} "
                    f"This one is going down to the wire."
                )
            return (
                f"Final quarter. {score_line} "
                f"{lead_team} looking to close it out."
            )

        # OT
        return (
            f"Overtime! {score_line} "
            f"Couldn't settle it in regulation."
        )

    def halftime_report(self, arc_snapshot: ArcSnapshot) -> str:
        """Generate a structured halftime breakdown.

        Score, player of the half, tactical observation, second half preview.
        """
        lines: List[str] = []

        # Score
        lines.append(f"HALFTIME: {self._score_line()}")

        # Player of the half
        top = self._top_scorer()
        if top:
            name, pts, shooting = top
            lines.append(
                f"Player of the half: {name} with {pts} points ({shooting})."
            )

        # Team shooting
        home_pct = self.stats.home_stats.fg_pct
        away_pct = self.stats.away_stats.fg_pct
        lines.append(
            f"Shooting: {self.home_team} {home_pct * 100:.0f}% FG, "
            f"{self.away_team} {away_pct * 100:.0f}% FG."
        )

        # Second half preview
        lead_team, margin = self._lead_info()
        if margin <= 5:
            lines.append("This one is tight. Should be a great second half.")
        elif margin >= 15:
            lines.append(
                f"{lead_team} in control. Can {self._trailing_team()} "
                f"make a run in the second half?"
            )
        else:
            lines.append(
                f"{self._trailing_team()} needs to find something "
                f"different in the second half."
            )

        return " ".join(lines)

    def end_of_game_wrap(self, arc_snapshot: ArcSnapshot) -> str:
        """Generate an end-of-game summary.

        Final score, player of the game, key moment, narrative summary.
        """
        lines: List[str] = []

        # Final score
        winner, margin = self._lead_info()
        lines.append(
            f"FINAL: {self.home_team} {self.stats.home_score}, "
            f"{self.away_team} {self.stats.away_score}."
        )

        # Player of the game
        top = self._top_scorer()
        if top:
            name, pts, shooting = top
            pstats = None
            for pid, ps in self.stats.players.items():
                if ps.player_name == name:
                    pstats = ps
                    break
            if pstats:
                lines.append(
                    f"Player of the game: {name} -- {pstats.stat_line()} "
                    f"({shooting})."
                )
            else:
                lines.append(
                    f"Player of the game: {name} with {pts} points."
                )

        # Game summary
        if margin <= 5:
            lines.append("What a game. Came down to the wire.")
        elif margin >= 20:
            lines.append(f"{winner} dominated from start to finish.")
        else:
            lines.append(f"{winner} pulls away for the win.")

        return " ".join(lines)

    def _score_line(self) -> str:
        """Current score as a string."""
        return (
            f"{self.home_team} {self.stats.home_score}, "
            f"{self.away_team} {self.stats.away_score}."
        )

    def _lead_info(self) -> tuple:
        """Return (leading_team, margin)."""
        diff = self.stats.home_score - self.stats.away_score
        if diff >= 0:
            return self.home_team, diff
        return self.away_team, -diff

    def _trailing_team(self) -> str:
        """Return the trailing team name."""
        lead_team, _ = self._lead_info()
        return self.away_team if lead_team == self.home_team else self.home_team

    def _top_scorer(self) -> Optional[tuple]:
        """Return (name, points, shooting_line) for the top scorer."""
        if not self.stats.players:
            return None
        top = max(self.stats.players.values(), key=lambda p: p.points)
        if top.points == 0:
            return None
        return (top.player_name, top.points, top.shooting_line())

    def _top_performer_line(self) -> str:
        """One-line summary of the top performer so far."""
        top = self._top_scorer()
        if not top:
            return ""
        name, pts, shooting = top
        return f"{name} leads the way with {pts} points."
