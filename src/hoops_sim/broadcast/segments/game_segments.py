"""Broadcast segment generators for game structure moments.

Generates text for: game open, quarter intros, halftime report,
clock callouts, and game end.
"""

from __future__ import annotations

import random
from typing import Optional


class GameSegments:
    """Generates broadcast segments for game structure moments."""

    def __init__(
        self,
        home_team: str,
        away_team: str,
        rng: Optional[random.Random] = None,
    ) -> None:
        self._home = home_team
        self._away = away_team
        self._rng = rng or random.Random()

    def game_open(self) -> str:
        """Generate the game opening broadcast."""
        templates = [
            (
                f"Good evening, everyone! Tonight, the {self._home} host the {self._away}. "
                "Should be a great one."
            ),
            (
                f"Welcome to tonight's matchup -- the {self._away} visiting the {self._home}. "
                "Let's get into it."
            ),
            (
                f"We're live for {self._away} at {self._home}! "
                "Tip-off is moments away."
            ),
            (
                f"It's game night! The {self._home} take on the {self._away}. "
                "Both teams looking to make a statement tonight."
            ),
        ]
        return self._rng.choice(templates)

    def quarter_intro(
        self, quarter: int, home_score: int, away_score: int,
    ) -> str:
        """Generate a quarter introduction."""
        if quarter == 2:
            return self._second_quarter_intro(home_score, away_score)
        if quarter == 3:
            return self._third_quarter_intro(home_score, away_score)
        if quarter == 4:
            return self._fourth_quarter_intro(home_score, away_score)
        if quarter > 4:
            return self._overtime_intro(quarter, home_score, away_score)
        return ""

    def halftime_report(
        self,
        home_score: int,
        away_score: int,
        top_scorer_name: str = "",
        top_scorer_points: int = 0,
    ) -> str:
        """Generate the halftime report."""
        score_line = self._score_line(home_score, away_score)
        base = f"At the half, {score_line}."

        if top_scorer_name and top_scorer_points > 0:
            base += f" {top_scorer_name} leads all scorers with {top_scorer_points}."

        if abs(home_score - away_score) <= 5:
            base += " It's been a tight one so far."
        elif abs(home_score - away_score) >= 15:
            leader = self._home if home_score > away_score else self._away
            base += f" {leader} in command at the break."

        return base

    def clock_callout(
        self, quarter: int, game_clock: float, home_score: int, away_score: int,
    ) -> str:
        """Generate clock callout for key moments."""
        margin = abs(home_score - away_score)
        leader = self._home if home_score > away_score else self._away

        if game_clock <= 120 and quarter == 4:
            if margin <= 5:
                return f"Under 2 minutes in the 4th, {leader} clinging to a {margin}-point lead."
            if margin <= 10:
                return f"Two minutes to go, {leader} up {margin}."
        if game_clock <= 300 and quarter == 4:
            return f"Under 5 minutes left in the 4th. {self._score_line(home_score, away_score)}."
        if game_clock <= 120:
            return f"Under 2 minutes in the {_quarter_name(quarter)}."

        return ""

    def game_end(
        self,
        home_score: int,
        away_score: int,
        top_scorer_name: str = "",
        top_scorer_points: int = 0,
    ) -> str:
        """Generate the game ending broadcast."""
        score_line = self._score_line(home_score, away_score)
        margin = abs(home_score - away_score)

        if margin <= 3:
            opener = self._rng.choice([
                "What a game!",
                "What a finish!",
                "Down to the wire!",
                "An absolute thriller!",
            ])
        elif margin >= 20:
            winner = self._home if home_score > away_score else self._away
            opener = self._rng.choice([
                f"{winner} cruise to victory.",
                f"A dominant performance by {winner}.",
                f"{winner} were in control from start to finish.",
            ])
        else:
            opener = self._rng.choice([
                "That'll do it.",
                "And that's the game.",
                "Final buzzer sounds.",
            ])

        result = f"{opener} FINAL: {score_line}."
        if top_scorer_name and top_scorer_points > 0:
            result += f" {top_scorer_name} led the way with {top_scorer_points} points."
        return result

    def _second_quarter_intro(self, home: int, away: int) -> str:
        return (
            f"Back for the second quarter. {self._score_line(home, away)}."
        )

    def _third_quarter_intro(self, home: int, away: int) -> str:
        templates = [
            f"Second half underway. {self._score_line(home, away)}.",
            f"Back from the break. {self._score_line(home, away)}.",
            f"Third quarter tips off. {self._score_line(home, away)}.",
        ]
        return self._rng.choice(templates)

    def _fourth_quarter_intro(self, home: int, away: int) -> str:
        margin = abs(home - away)
        if margin <= 8:
            return self._rng.choice([
                f"Here we go, 4th quarter. {self._score_line(home, away)}. This is going to be good.",
                f"Final quarter. {self._score_line(home, away)}. Buckle up.",
            ])
        return f"4th quarter. {self._score_line(home, away)}."

    def _overtime_intro(self, quarter: int, home: int, away: int) -> str:
        ot_num = quarter - 4
        if ot_num == 1:
            return f"We're going to overtime! Tied at {home}. 5 extra minutes."
        return f"We need another overtime! OT{ot_num} coming up."

    def _score_line(self, home: int, away: int) -> str:
        if home > away:
            return f"{self._home} {home}, {self._away} {away}"
        if away > home:
            return f"{self._away} {away}, {self._home} {home}"
        return f"Tied at {home}"


def _quarter_name(quarter: int) -> str:
    names = {1: "1st quarter", 2: "2nd quarter", 3: "3rd quarter", 4: "4th quarter"}
    if quarter in names:
        return names[quarter]
    ot = quarter - 4
    return f"OT{ot}" if ot > 1 else "overtime"
