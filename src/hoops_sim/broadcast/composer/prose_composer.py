"""Prose composer: turns a PossessionResult into flowing broadcast prose.

The composer works in 4 phases:
  Phase A: Setup (calm, scene-setting)
  Phase B: Action (building tension)
  Phase C: Climax (intensity-scaled explosion or deflation)
  Phase D: Aftermath (resolution, stats, color)

Each phase's output is controlled by the intensity level.
"""

from __future__ import annotations

import random
from typing import List, Optional

from hoops_sim.events.game_events import (
    ActionChainResult,
    DriveResult,
    PassResult,
    PossessionResult,
    ScreenResult,
    ShotResult,
)


class ProseComposer:
    """Composes broadcast prose from possession results."""

    def __init__(self, rng: Optional[random.Random] = None) -> None:
        self._rng = rng or random.Random()
        self._recent_templates: list[str] = []
        self._max_recent = 50

    def compose(self, possession: PossessionResult, intensity: float) -> str:
        """Compose full broadcast prose for a possession.

        Args:
            possession: The possession result to narrate.
            intensity: 0.0-1.0 intensity score.

        Returns:
            Complete broadcast prose string.
        """
        # Determine verbosity level
        if intensity < 0.15:
            return self._compose_condensed(possession, intensity)
        if intensity < 0.35:
            return self._compose_brief(possession, intensity)

        parts = []

        # Phase A: Setup
        setup = self._phase_setup(possession, intensity)
        if setup:
            parts.append(setup)

        # Phase B: Action
        action = self._phase_action(possession, intensity)
        if action:
            parts.append(action)

        # Phase C: Climax
        climax = self._phase_climax(possession, intensity)
        if climax:
            parts.append(climax)

        # Phase D: Aftermath
        aftermath = self._phase_aftermath(possession, intensity)
        if aftermath:
            parts.append(aftermath)

        return " ".join(parts)

    # -- Condensed formats (low intensity) ------------------------------------

    def _compose_condensed(self, p: PossessionResult, intensity: float) -> str:
        """One-liner for routine plays."""
        name = self._short_name(p.ball_handler)
        if p.shot and p.shot.made:
            shot_desc = self._brief_shot_type(p.shot)
            score = self._score_line(p)
            return f"{name} {shot_desc}. {score}"
        if p.shot and not p.shot.made:
            return f"{name} misses. {self._score_line(p)}"
        if p.turnover:
            return f"Turnover, {p.offensive_team}. {self._score_line(p)}"
        if p.violation:
            return f"{p.violation.violation_type.replace('_', ' ').title()}. {self._score_line(p)}"
        return f"{name} possession. {self._score_line(p)}"

    def _compose_brief(self, p: PossessionResult, intensity: float) -> str:
        """Brief narration for moderate plays."""
        parts = []
        name = self._short_name(p.ball_handler)

        # Brief setup
        if p.screen and p.screen.screener:
            parts.append(
                f"{name} uses the screen from {self._short_name(p.screen.screener)}."
            )
        elif p.drive and p.drive.driver:
            parts.append(f"{name} drives {p.drive.direction}.")

        # Climax
        if p.shot and p.shot.made:
            parts.append(f"{self._brief_shot_description(p.shot)}")
        elif p.shot and not p.shot.made:
            parts.append(f"{name} misses the {self._brief_shot_type(p.shot)}.")
            if p.rebound and p.rebound.rebounder:
                parts.append(
                    f"{self._short_name(p.rebound.rebounder)} with the board."
                )
        elif p.turnover:
            parts.append(self._brief_turnover(p))
        elif p.foul:
            parts.append(self._brief_foul(p))

        parts.append(self._score_line(p))
        return " ".join(parts)

    # -- Phase A: Setup -------------------------------------------------------

    def _phase_setup(self, p: PossessionResult, intensity: float) -> str:
        """Scene-setting: who has the ball, who's guarding them."""
        name = self._short_name(p.ball_handler)
        defender = self._short_name(p.primary_defender)

        if p.is_transition:
            templates = [
                f"{p.offensive_team} in transition, {name} pushing it up...",
                f"{name} leads the break!",
                f"Here comes {name} on the fast break...",
            ]
            return self._pick(templates)

        if defender and intensity >= 0.6:
            templates = [
                f"{name}, isolated on the left wing against {defender}...",
                f"{name}, sizes up {defender}...",
                f"{name} with the ball, {defender} guarding him...",
                f"{name} on the wing, {defender} checking him closely...",
            ]
            return self._pick(templates)

        if p.screen and p.screen.screener:
            screener = self._short_name(p.screen.screener)
            templates = [
                f"{name} calls for the screen from {screener}.",
                f"{screener} comes up to set the pick for {name}.",
                f"{name}, ball screen from {screener}...",
            ]
            return self._pick(templates)

        templates = [
            f"{name} with the ball...",
            f"{name} at the top of the key...",
            f"{p.offensive_team} running their offense, {name} orchestrating...",
        ]
        return self._pick(templates)

    # -- Phase B: Action ------------------------------------------------------

    def _phase_action(self, p: PossessionResult, intensity: float) -> str:
        """Building tension: dribble moves, drives, passes."""
        parts = []

        # Action chain narration
        if p.action_chain and p.action_chain.moves:
            chain_text = self._narrate_action_chain(p.action_chain, intensity)
            if chain_text:
                parts.append(chain_text)

        # Screen narration
        if p.screen and p.screen.effective and not parts:
            parts.append(self._narrate_screen(p.screen, intensity))

        # Pass chain narration
        if p.passes and intensity >= 0.5:
            pass_text = self._narrate_passes(p.passes, intensity)
            if pass_text:
                parts.append(pass_text)

        # Drive narration
        if p.drive:
            drive_text = self._narrate_drive(p.drive, intensity)
            if drive_text:
                parts.append(drive_text)

        return " ".join(parts) if parts else ""

    def _narrate_action_chain(
        self, chain: ActionChainResult, intensity: float,
    ) -> str:
        """Narrate a dribble move chain with defender reactions."""
        if not chain.moves:
            return ""

        player = self._short_name(chain.player)
        defender = self._short_name(chain.defender)
        parts = []

        for move in chain.moves:
            move_name = move.move_type.replace("_", " ")
            if move.success and move.defender_reaction:
                reaction = move.defender_reaction
                if intensity >= 0.7:
                    parts.append(
                        f"{move_name} -- {defender} {reaction}!"
                    )
                else:
                    parts.append(f"hits the {move_name}, {defender} {reaction}")
            elif move.success:
                parts.append(f"{move_name}")
            else:
                parts.append(f"tries the {move_name}")

        if chain.outcome == "ankle_breaker" and intensity >= 0.7:
            parts.append(f"{defender} goes DOWN!")
            return f"{player} " + ", ".join(parts[:-1]) + " " + parts[-1]

        if chain.outcome == "separation" and intensity >= 0.5:
            parts.append("creates space")

        text = ", ".join(parts) if parts else ""
        return f"{player} {text}" if text else ""

    def _narrate_screen(self, screen: ScreenResult, intensity: float) -> str:
        """Narrate a screen action."""
        handler = self._short_name(screen.ball_handler)
        screener = self._short_name(screen.screener)

        if screen.switch_occurred and screen.new_defender:
            new_def = self._short_name(screen.new_defender)
            return (
                f"{screener} sets the pick, they switch -- "
                f"{handler} now has {new_def} on him."
            )
        if screen.defender_got_screened:
            defender = self._short_name(screen.defender)
            return (
                f"{screener} with a solid screen, {defender} gets caught up."
            )
        return f"{handler} uses the screen from {screener}."

    def _narrate_passes(self, passes: List[PassResult], intensity: float) -> str:
        """Narrate a pass chain."""
        if not passes:
            return ""
        if len(passes) == 1:
            p = passes[0]
            passer = self._short_name(p.passer)
            receiver = self._short_name(p.receiver)
            templates = [
                f"{passer} finds {receiver}",
                f"{passer} swings it to {receiver}",
                f"kick-out to {receiver}",
            ]
            return self._pick(templates)
        # Multi-pass ball movement
        names = [self._short_name(p.passer) for p in passes]
        names.append(self._short_name(passes[-1].receiver))
        chain = " to ".join(names)
        if intensity >= 0.6:
            return f"Beautiful ball movement -- {chain}!"
        return f"{chain}."

    def _narrate_drive(self, drive: DriveResult, intensity: float) -> str:
        """Narrate a drive to the basket."""
        driver = self._short_name(drive.driver)
        direction = drive.direction or "the lane"

        if drive.drew_help and drive.help_defender:
            helper = self._short_name(drive.help_defender)
            if intensity >= 0.6:
                return (
                    f"drives {direction}, {helper} comes to help!"
                )
            return f"drives, {helper} rotates over."

        if drive.got_to_rim and intensity >= 0.6:
            templates = [
                f"drives hard {direction}, gets to the rim!",
                f"attacks {direction}, all the way to the cup!",
                f"powers {direction} into the paint!",
            ]
            return self._pick(templates)

        return f"drives {direction}."

    # -- Phase C: Climax ------------------------------------------------------

    def _phase_climax(self, p: PossessionResult, intensity: float) -> str:
        """The moment of truth: shot result, turnover, foul."""
        if p.shot:
            return self._narrate_shot_climax(p.shot, intensity)
        if p.turnover:
            return self._narrate_turnover_climax(p, intensity)
        if p.foul:
            return self._narrate_foul_climax(p, intensity)
        if p.violation:
            return self._narrate_violation(p.violation.violation_type)
        return ""

    def _narrate_shot_climax(self, shot: ShotResult, intensity: float) -> str:
        """Narrate the shot result with intensity-appropriate language."""
        shooter = self._short_name(shot.shooter)

        if shot.made:
            return self._narrate_made_shot(shot, intensity)
        return self._narrate_missed_shot(shot, intensity)

    def _narrate_made_shot(self, shot: ShotResult, intensity: float) -> str:
        """Narrate a made shot."""
        shooter = self._short_name(shot.shooter)

        # Dunks
        if shot.is_dunk:
            if intensity >= 0.8:
                templates = [
                    f"{shooter} THROWS IT DOWN! WHAT A SLAM!",
                    f"POSTER! {shooter} WITH THE MONSTER JAM!",
                    f"{shooter} RISES UP AND HAMMERS IT HOME!",
                    f"OH MY! {shooter} WITH THE THUNDEROUS DUNK!",
                ]
            elif intensity >= 0.5:
                templates = [
                    f"{shooter} dunks it!",
                    f"{shooter} finishes with the slam!",
                    f"{shooter} throws it down!",
                ]
            else:
                templates = [
                    f"{shooter} dunks it home.",
                    f"{shooter} with the easy slam.",
                ]
            return self._pick(templates)

        # Three pointers
        if shot.points == 3:
            if intensity >= 0.85:
                templates = [
                    f"DRAINS THE THREE! {shooter} FROM DOWNTOWN!",
                    f"BANG! {shooter} BURIES THE THREE!",
                    f"{shooter} pulls up... GOT IT! BANG!",
                    f"{shooter} for THREE... YES! WHAT A SHOT!",
                    f"ARE YOU KIDDING ME?! {shooter} FROM DEEP!",
                    f"{shooter}... BANG! FROM WAY DOWNTOWN!",
                ]
            elif intensity >= 0.6:
                templates = [
                    f"{shooter} knocks down the three!",
                    f"{shooter} drills it from deep!",
                    f"{shooter} buries the three!",
                    f"{shooter}, the three is good!",
                    f"{shooter} catches and fires -- got it!",
                ]
            elif intensity >= 0.35:
                templates = [
                    f"{shooter} hits the three.",
                    f"{shooter} from three. Good.",
                    f"Three-pointer, {shooter}.",
                    f"{shooter} connects from deep.",
                ]
            else:
                templates = [f"{shooter} with the three."]
            return self._pick(templates)

        # Mid-range and layups
        ft = shot.finish_type or shot.shot_type or "jumper"
        ft_clean = ft.replace("_", " ")

        if intensity >= 0.7:
            if "layup" in ft or "finger_roll" in ft or "reverse" in ft:
                templates = [
                    f"{shooter} finishes with the {ft_clean}!",
                    f"{shooter}, beautiful {ft_clean}! So smooth!",
                    f"{shooter} lays it in! What a touch!",
                ]
            else:
                templates = [
                    f"{shooter} with the {ft_clean}... got it!",
                    f"{shooter} pulls up, {ft_clean}... GOOD!",
                    f"{shooter} drains the {ft_clean}!",
                ]
        elif intensity >= 0.35:
            templates = [
                f"{shooter} with the {ft_clean}. Good.",
                f"{shooter} hits the {ft_clean}.",
                f"{shooter} scores on the {ft_clean}.",
            ]
        else:
            templates = [f"{shooter} {ft_clean}. Good."]

        return self._pick(templates)

    def _narrate_missed_shot(self, shot: ShotResult, intensity: float) -> str:
        """Narrate a missed shot."""
        shooter = self._short_name(shot.shooter)

        if shot.shot_result_type == "airball":
            if intensity >= 0.5:
                return f"{shooter} shoots... AIRBALL! Oh no."
            return f"{shooter} airballs it."

        if shot.shot_result_type == "blocked":
            defender = self._short_name(shot.defender)
            if intensity >= 0.7:
                templates = [
                    f"{shooter} goes up... BLOCKED! {defender} rejects it!",
                    f"DENIED! {defender} swats it away!",
                    f"{shooter} tries to finish -- BLOCKED by {defender}!",
                ]
            else:
                templates = [
                    f"{shooter} blocked by {defender}.",
                    f"{defender} with the block.",
                ]
            return self._pick(templates)

        if intensity >= 0.5:
            templates = [
                f"{shooter} misses the shot.",
                f"No good! {shooter} can't connect.",
                f"{shooter} fires but it rims out.",
                f"Off the mark from {shooter}.",
            ]
        else:
            templates = [
                f"{shooter} misses.",
                f"No good from {shooter}.",
            ]
        return self._pick(templates)

    def _narrate_turnover_climax(
        self, p: PossessionResult, intensity: float,
    ) -> str:
        """Narrate a turnover."""
        handler = self._short_name(p.ball_handler)
        to = p.turnover
        if not to:
            return f"Turnover, {p.offensive_team}."

        if to.turnover_type == "steal" and to.stealer:
            stealer = self._short_name(to.stealer)
            if intensity >= 0.6:
                templates = [
                    f"{stealer} STRIPS IT! Steal!",
                    f"PICKED OFF by {stealer}!",
                    f"{stealer} jumps the passing lane! Steal!",
                    f"Ripped away by {stealer}!",
                ]
            else:
                templates = [
                    f"Stolen by {stealer}.",
                    f"{stealer} with the steal.",
                ]
            return self._pick(templates)

        if to.turnover_type == "bad_pass":
            return f"Bad pass by {handler}. Turnover."
        if to.turnover_type == "travel":
            return f"Traveling on {handler}."
        if to.turnover_type == "out_of_bounds":
            return f"{handler} steps out of bounds. Turnover."
        if to.turnover_type == "offensive_foul":
            return f"Offensive foul on {handler}."

        return f"Turnover, {p.offensive_team}."

    def _narrate_foul_climax(
        self, p: PossessionResult, intensity: float,
    ) -> str:
        """Narrate a foul and free throws."""
        foul = p.foul
        if not foul:
            return "Foul called."

        fouler = self._short_name(foul.fouler)
        fouled = self._short_name(foul.fouled_player)

        line = f"Foul on {fouler}."
        if foul.is_foul_trouble:
            line += f" That's {foul.fouler_foul_count} fouls now -- he's in trouble."

        if foul.free_throws_awarded > 0:
            made = foul.free_throws_made
            total = foul.free_throws_awarded
            if made == total:
                line += f" {fouled} hits {_num_word(made)} of {_num_word(total)} from the line."
            elif made == 0:
                line += f" {fouled} misses {_num_word(total)} at the line."
            else:
                line += f" {fouled} makes {_num_word(made)} of {_num_word(total)}."

        return line

    def _narrate_violation(self, violation_type: str) -> str:
        """Narrate a violation."""
        vt = violation_type.replace("_", " ").title()
        return f"{vt} violation."

    # -- Phase D: Aftermath ---------------------------------------------------

    def _phase_aftermath(self, p: PossessionResult, intensity: float) -> str:
        """Resolution: score, rebound, stats, color commentary."""
        parts = []

        # Rebound narration
        if p.rebound and p.rebound.rebounder:
            reb = p.rebound
            rebounder = self._short_name(reb.rebounder)
            if reb.is_offensive:
                if intensity >= 0.6:
                    parts.append(
                        f"{rebounder} grabs the offensive board!"
                    )
                else:
                    parts.append(
                        f"Offensive rebound, {rebounder}."
                    )
            else:
                if intensity >= 0.4:
                    parts.append(
                        f"{rebounder} pulls down the rebound."
                    )

        # Score line (only for made shots at higher intensity)
        if p.scored and intensity >= 0.35:
            parts.append(self._score_line(p))

        # Scoring run callout
        if p.momentum.scoring_run >= 8 and intensity >= 0.5:
            team = p.momentum.run_team
            run = p.momentum.scoring_run
            parts.append(
                f"That's a {run}-0 run for {team}!"
            )

        return " ".join(parts) if parts else ""

    # -- Helpers --------------------------------------------------------------

    def _short_name(self, ref) -> str:
        """Get a short display name from a PlayerRef or None."""
        if ref is None:
            return "Unknown"
        name = ref.name
        if not name:
            return "Unknown"
        parts = name.split()
        if len(parts) >= 2:
            return parts[-1]  # Last name
        return name

    def _brief_shot_type(self, shot: ShotResult) -> str:
        """Return a brief shot type description."""
        if shot.is_dunk:
            return "slam"
        if shot.points == 3:
            return "three"
        ft = shot.finish_type or shot.shot_type or "jumper"
        return ft.replace("_", " ")

    def _brief_shot_description(self, shot: ShotResult) -> str:
        """Brief made shot description."""
        shooter = self._short_name(shot.shooter)
        desc = self._brief_shot_type(shot)
        return f"{shooter} with the {desc}."

    def _brief_turnover(self, p: PossessionResult) -> str:
        handler = self._short_name(p.ball_handler)
        if p.turnover and p.turnover.stealer:
            return (
                f"Stolen by {self._short_name(p.turnover.stealer)}."
            )
        return f"Turnover, {handler}."

    def _brief_foul(self, p: PossessionResult) -> str:
        if not p.foul:
            return "Foul called."
        fouler = self._short_name(p.foul.fouler)
        return f"Foul on {fouler}."

    def _score_line(self, p: PossessionResult) -> str:
        """Generate a score line like 'Celtics 54, Knicks 50.'"""
        s = p.score
        home = s.home_score_after or s.home_score
        away = s.away_score_after or s.away_score
        if home > away:
            return f"{s.home_team} {home}, {s.away_team} {away}."
        if away > home:
            return f"{s.away_team} {away}, {s.home_team} {home}."
        return f"Tied at {home}."

    def _pick(self, templates: list[str]) -> str:
        """Pick a template that hasn't been used recently."""
        # Filter out recently used templates
        available = [t for t in templates if t not in self._recent_templates]
        if not available:
            available = templates
            self._recent_templates = []

        choice = self._rng.choice(available)
        self._recent_templates.append(choice)
        if len(self._recent_templates) > self._max_recent:
            self._recent_templates.pop(0)
        return choice


def _num_word(n: int) -> str:
    """Convert small number to word."""
    words = {1: "one", 2: "two", 3: "three", 4: "four"}
    return words.get(n, str(n))
