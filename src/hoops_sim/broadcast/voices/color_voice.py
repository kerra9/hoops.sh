"""Color commentary announcer voice.

Past tense analysis, references earlier plays, provides stats and matchup insight.
Only fires on notable+ plays. Adds depth and context to PBP calls.
"""

from __future__ import annotations

import random
from typing import List, Optional

from hoops_sim.events.game_events import PossessionResult


class ColorVoice:
    """Color commentary analyst voice.

    Characteristics:
    - Past tense analysis: "That was a great read", "He saw the lane open"
    - References earlier plays and patterns
    - Provides stats context ("His 4th three tonight")
    - Matchup insight ("He's got 3 inches on the smaller defender")
    - Analytical but enthusiastic at high intensity
    """

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self._used_themes: list[str] = []
        self._max_theme_cooldown = 5

    def comment(
        self,
        possession: PossessionResult,
        intensity: float,
        player_points: int = 0,
        player_field_goals: int = 0,
        player_threes: int = 0,
    ) -> str:
        """Generate color commentary for a possession.

        Only called for notable+ plays (intensity >= 0.5).
        Returns empty string if nothing worth commenting on.
        """
        comments: list[str] = []

        # Stat weaving
        stat_comment = self._weave_stats(
            possession, player_points, player_field_goals, player_threes,
        )
        if stat_comment:
            comments.append(stat_comment)

        # Play quality analysis
        quality = self._analyze_play(possession, intensity)
        if quality:
            comments.append(quality)

        # Matchup analysis
        matchup = self._analyze_matchup(possession, intensity)
        if matchup:
            comments.append(matchup)

        # Scoring run commentary
        run = self._comment_on_run(possession)
        if run:
            comments.append(run)

        # Foul trouble commentary
        foul = self._comment_on_fouls(possession)
        if foul:
            comments.append(foul)

        if not comments:
            return ""

        # Pick the most relevant comment (or two for high intensity)
        if intensity >= 0.8 and len(comments) >= 2:
            return " ".join(comments[:2])
        return comments[0]

    def _weave_stats(
        self,
        p: PossessionResult,
        points: int,
        field_goals: int,
        threes: int,
    ) -> str:
        """Weave stats into commentary naturally."""
        if not p.shot or not p.shot.made:
            return ""

        shooter = self._short_name(p.ball_handler)
        new_points = points + p.shot.points

        # Scoring milestones
        for milestone in [50, 40, 30, 20]:
            if points < milestone <= new_points:
                if milestone >= 40:
                    return f"That gives {shooter} {new_points}! What a performance!"
                if milestone >= 30:
                    return f"{shooter} now with {new_points} points. He's been fantastic."
                return f"That's {new_points} for {shooter}."

        # Three-point shooting
        if p.shot.points == 3:
            new_threes = threes + 1
            if new_threes >= 6:
                return self._with_cooldown(
                    "hot_shooting",
                    f"That's {new_threes} threes for {shooter} tonight. He's unconscious!",
                )
            if new_threes >= 4:
                return self._with_cooldown(
                    "hot_shooting",
                    f"{shooter}'s {_ordinal(new_threes)} three tonight. He's on fire.",
                )

        return ""

    def _analyze_play(self, p: PossessionResult, intensity: float) -> str:
        """Analyze the quality of the play."""
        if p.action_chain and p.action_chain.outcome == "ankle_breaker":
            return self._with_cooldown(
                "ankle_breaker",
                "Oh my goodness, look at that separation! The defender had no chance.",
            )

        if p.shot and p.shot.is_and_one:
            return self._with_cooldown(
                "and_one",
                "And the foul! That's an old-fashioned three-point play.",
            )

        if p.shot and p.shot.made and p.shot.contest_level == "heavily_contested":
            return self._with_cooldown(
                "tough_shot",
                "That was a TOUGH shot. Great defense, better offense.",
            )

        if p.passes and len(p.passes) >= 3:
            return self._with_cooldown(
                "ball_movement",
                "Beautiful ball movement there. That's unselfish basketball.",
            )

        return ""

    def _analyze_matchup(self, p: PossessionResult, intensity: float) -> str:
        """Provide matchup insight."""
        if intensity < 0.6:
            return ""

        if p.screen and p.screen.switch_occurred and p.screen.new_defender:
            new_def = self._short_name(p.screen.new_defender)
            handler = self._short_name(p.ball_handler)
            return self._with_cooldown(
                "mismatch",
                f"They got the switch they wanted -- {handler} now has {new_def} on him.",
            )

        return ""

    def _comment_on_run(self, p: PossessionResult) -> str:
        """Comment on scoring runs."""
        run = p.momentum.scoring_run
        team = p.momentum.run_team

        if run >= 12:
            return self._with_cooldown(
                "scoring_run",
                f"That's a {run}-0 run for {team}! The other team has to stop the bleeding.",
            )
        if run >= 8:
            return self._with_cooldown(
                "scoring_run",
                f"{run}-0 run. {team} is rolling right now.",
            )
        return ""

    def _comment_on_fouls(self, p: PossessionResult) -> str:
        """Comment on foul trouble situations."""
        if not p.foul:
            return ""

        foul = p.foul
        if foul.is_foul_trouble and foul.fouler:
            fouler = self._short_name(foul.fouler)
            count = foul.fouler_foul_count
            if count >= 5:
                return f"{fouler} picks up his {_ordinal(count)} foul. One more and he's done."
            if count == 4:
                return f"That's 4 on {fouler}. The coach has to think about taking him out."
            if count == 3 and p.clock.quarter <= 2:
                return f"Third foul on {fouler} before the half. He'll have to sit."
        return ""

    def _with_cooldown(self, theme: str, text: str) -> str:
        """Return text only if the theme hasn't been used recently."""
        if theme in self._used_themes:
            return ""
        self._used_themes.append(theme)
        if len(self._used_themes) > self._max_theme_cooldown:
            self._used_themes.pop(0)
        return text

    def _short_name(self, ref) -> str:
        if ref is None:
            return "Unknown"
        name = ref.name
        if not name:
            return "Unknown"
        parts = name.split()
        return parts[-1] if len(parts) >= 2 else name


def _ordinal(n: int) -> str:
    """Convert number to ordinal string."""
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        suffix = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suffix}"
