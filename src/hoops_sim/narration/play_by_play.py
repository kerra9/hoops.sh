"""Play-by-play narrator: handles real-time action description.

Narrates the full possession flow -- not just the terminal event,
but the dribble moves, screens, passes, drives, and shots that
compose a possession. Uses the ActionChainTracker to weave
micro-actions into coherent multi-sentence possession narratives.
"""

from __future__ import annotations

from typing import List, Optional

from hoops_sim.narration.events import (
    BallAdvanceEvent,
    BaseNarrationEvent,
    BlockEvent,
    DribbleMoveEvent,
    DriveEvent,
    FoulEvent,
    FreeThrowEvent,
    MomentumEvent,
    NarrationEventType,
    PassEvent,
    PossessionStartEvent,
    QuarterBoundaryEvent,
    QuarterEventKind,
    ReboundEvent,
    ScreenEvent,
    ShotResultEvent,
    SubstitutionEvent,
    TimeoutEvent,
    TurnoverEvent,
)
from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.narration.templates.ball_advance import (
    AFTER_MADE_BASKET_TEMPLATES,
    AFTER_TIMEOUT_TEMPLATES,
    TRANSITION_PUSH_TEMPLATES,
    WALK_IT_UP_TEMPLATES,
)
from hoops_sim.narration.templates.dead_ball import (
    BETWEEN_QUARTER_TEMPLATES,
    FREE_THROW_MADE_TEMPLATES,
    FREE_THROW_MISSED_TEMPLATES,
    HALFTIME_TEMPLATES,
    SUBSTITUTION_TEMPLATES,
    TIMEOUT_TEMPLATES,
)
from hoops_sim.narration.templates.defense import (
    BLOCK_TEMPLATES,
    STEAL_TEMPLATES,
)
from hoops_sim.narration.templates.dribble_moves import (
    ANKLE_BREAKER_TEMPLATES,
    COMBO_CHAIN_TEMPLATES,
    DRIBBLE_TEMPLATES_BY_TYPE,
)
from hoops_sim.narration.templates.drives import (
    DRIVE_INITIATION_TEMPLATES,
    DUNK_TEMPLATES,
    FINISH_TEMPLATES_BY_TYPE,
    KICK_OUT_FROM_DRIVE_TEMPLATES,
    POSTER_DUNK_TEMPLATES,
)
from hoops_sim.narration.templates.passes import (
    ENTRY_PASS_TEMPLATES,
    KICK_OUT_TEMPLATES,
    PASS_TEMPLATES_BY_TYPE,
    SKIP_PASS_TEMPLATES,
)
from hoops_sim.narration.templates.screens import (
    DEFENDER_GOES_OVER,
    DEFENDER_GOES_UNDER,
    DROP_COVERAGE_TEMPLATES,
    HEDGE_TEMPLATES,
    POP_TEMPLATES,
    ROLL_TEMPLATES,
    SCREEN_SET_TEMPLATES,
    SWITCH_TEMPLATES,
)
from hoops_sim.narration.templates.shots import (
    AND_ONE_SUFFIX,
    CLOSE_RANGE_MADE,
    CLOSE_RANGE_MISSED,
    CORNER_THREE_MADE,
    MID_RANGE_MADE,
    MID_RANGE_MISSED,
    SCORE_UPDATE_TEMPLATES,
    THREE_POINTER_MADE,
    THREE_POINTER_MISSED,
    TIE_SCORE_TEMPLATES,
)
from hoops_sim.utils.rng import SeededRNG


class PlayByPlayNarrator:
    """Generates play-by-play narration text from rich narration events.

    Narrates the full possession flow. Adjusts verbosity based on
    game pace -- terse in transition, detailed in half-court.
    """

    def __init__(self, rng: SeededRNG, stat_tracker: LiveStatTracker) -> None:
        self.rng = rng
        self.stats = stat_tracker
        self._recent_templates: List[str] = []
        self._max_recent = 20

    def narrate(self, event: BaseNarrationEvent) -> Optional[str]:
        """Produce play-by-play text for a narration event.

        Returns None if the event doesn't warrant PBP narration.
        """
        handler = self._HANDLERS.get(event.event_type)
        if handler is None:
            return None
        return handler(self, event)

    def _pick_template(self, templates: List[str]) -> str:
        """Select a template, avoiding recent repeats."""
        # Filter out recently used
        available = [t for t in templates if t not in self._recent_templates]
        if not available:
            available = templates
        choice = self.rng.choice(available)
        self._recent_templates.append(choice)
        if len(self._recent_templates) > self._max_recent:
            self._recent_templates.pop(0)
        return choice

    # -- Event handlers -------------------------------------------------------

    def _narrate_possession_start(self, event: PossessionStartEvent) -> Optional[str]:
        return None  # Handled at possession level, not individual event

    def _narrate_ball_advance(self, event: BallAdvanceEvent) -> Optional[str]:
        if event.is_transition:
            tmpl = self._pick_template(TRANSITION_PUSH_TEMPLATES)
        elif event.is_after_timeout:
            tmpl = self._pick_template(AFTER_TIMEOUT_TEMPLATES)
        elif event.is_after_made_basket:
            tmpl = self._pick_template(AFTER_MADE_BASKET_TEMPLATES)
        else:
            tmpl = self._pick_template(WALK_IT_UP_TEMPLATES)
        return tmpl.format(
            handler=event.ball_handler_name,
            team="",
            play="",
            receiver=event.ball_handler_name,
        )

    def _narrate_dribble_move(self, event: DribbleMoveEvent) -> Optional[str]:
        if event.ankle_breaker:
            tmpl = self._pick_template(ANKLE_BREAKER_TEMPLATES)
            return tmpl.format(
                player=event.player_name,
                move=event.move_type,
                defender=event.defender_name or "the defender",
            )

        move_key = event.move_type
        templates_pair = DRIBBLE_TEMPLATES_BY_TYPE.get(move_key)
        if templates_pair is None:
            return None

        success_templates, fail_templates = templates_pair
        if event.success:
            tmpl = self._pick_template(success_templates)
        else:
            tmpl = self._pick_template(fail_templates)

        if event.combo_count >= 2:
            combo = self._pick_template(COMBO_CHAIN_TEMPLATES)
            prefix = combo.format(
                player=event.player_name,
                defender=event.defender_name or "the defender",
            )
            main = tmpl.format(
                player=event.player_name,
                defender=event.defender_name or "the defender",
            )
            return f"{prefix} {main}"

        return tmpl.format(
            player=event.player_name,
            defender=event.defender_name or "the defender",
        )

    def _narrate_screen(self, event: ScreenEvent) -> Optional[str]:
        parts = []

        # Screen set
        tmpl = self._pick_template(SCREEN_SET_TEMPLATES)
        parts.append(tmpl.format(
            screener=event.screener_name,
            handler=event.handler_name,
        ))

        # Defender reaction
        if event.pnr_coverage == "switch":
            tmpl = self._pick_template(SWITCH_TEMPLATES)
            parts.append(tmpl.format(
                big=event.screener_name,
                handler=event.handler_name,
                defender="",
            ))
        elif event.pnr_coverage == "drop":
            tmpl = self._pick_template(DROP_COVERAGE_TEMPLATES)
            parts.append(tmpl.format(big=event.screener_name))
        elif event.pnr_coverage == "hedge":
            tmpl = self._pick_template(HEDGE_TEMPLATES)
            parts.append(tmpl.format(
                big=event.screener_name,
                handler=event.handler_name,
            ))
        elif event.defender_reaction == "over":
            tmpl = self._pick_template(DEFENDER_GOES_OVER)
            parts.append(tmpl.format(
                defender="The defender",
                handler=event.handler_name,
                screener=event.screener_name,
            ))
        elif event.defender_reaction == "under":
            tmpl = self._pick_template(DEFENDER_GOES_UNDER)
            parts.append(tmpl.format(
                defender="The defender",
                handler=event.handler_name,
            ))

        # Roll or pop
        if event.roller_or_popper == "roll":
            tmpl = self._pick_template(ROLL_TEMPLATES)
            parts.append(tmpl.format(
                screener=event.screener_name,
                handler=event.handler_name,
            ))
        elif event.roller_or_popper == "pop":
            tmpl = self._pick_template(POP_TEMPLATES)
            parts.append(tmpl.format(
                screener=event.screener_name,
                handler=event.handler_name,
            ))

        return " ".join(parts) if parts else None

    def _narrate_pass(self, event: PassEvent) -> Optional[str]:
        if event.is_kick_out:
            tmpl = self._pick_template(KICK_OUT_TEMPLATES)
        elif event.is_skip_pass:
            tmpl = self._pick_template(SKIP_PASS_TEMPLATES)
        elif event.is_entry_pass:
            tmpl = self._pick_template(ENTRY_PASS_TEMPLATES)
        else:
            pass_key = event.pass_type
            templates = PASS_TEMPLATES_BY_TYPE.get(pass_key)
            if templates:
                tmpl = self._pick_template(templates)
            else:
                tmpl = "{passer} passes to {receiver}."

        return tmpl.format(
            passer=event.passer_name,
            receiver=event.receiver_name,
        )

    def _narrate_drive(self, event: DriveEvent) -> Optional[str]:
        parts = []
        tmpl = self._pick_template(DRIVE_INITIATION_TEMPLATES)
        parts.append(tmpl.format(
            player=event.driver_name,
            defender=event.defender_name or "the defender",
        ))

        if event.kick_out and event.kick_out_target:
            tmpl = self._pick_template(KICK_OUT_FROM_DRIVE_TEMPLATES)
            parts.append(tmpl.format(
                driver=event.driver_name,
                receiver=event.kick_out_target,
            ))

        return " ".join(parts)

    def _narrate_shot_result(self, event: ShotResultEvent) -> Optional[str]:
        parts = []

        if event.made:
            if event.is_dunk:
                if event.finish_type == "poster":
                    tmpl = self._pick_template(POSTER_DUNK_TEMPLATES)
                    parts.append(tmpl.format(
                        player=event.shooter_name,
                        defender="the defender",
                    ))
                else:
                    tmpl = self._pick_template(DUNK_TEMPLATES)
                    parts.append(tmpl.format(player=event.shooter_name))
            elif event.finish_type and event.finish_type in FINISH_TEMPLATES_BY_TYPE:
                made_tmpls, _ = FINISH_TEMPLATES_BY_TYPE[event.finish_type]
                tmpl = self._pick_template(made_tmpls)
                parts.append(tmpl.format(
                    player=event.shooter_name,
                    result="good",
                    defender="the defender",
                ))
            elif event.is_three:
                zone_lower = event.zone.lower()
                if "corner" in zone_lower:
                    tmpl = self._pick_template(CORNER_THREE_MADE)
                else:
                    tmpl = self._pick_template(THREE_POINTER_MADE)
                parts.append(tmpl.format(
                    shooter=event.shooter_name,
                    team=event.team_name,
                    lead=abs(event.lead),
                ))
            elif event.distance < 8.0:
                tmpl = self._pick_template(CLOSE_RANGE_MADE)
                dist_str = "at the rim" if event.distance < 4.0 else f"{event.distance:.0f} feet out"
                parts.append(tmpl.format(
                    shooter=event.shooter_name,
                    distance=dist_str,
                ))
            else:
                tmpl = self._pick_template(MID_RANGE_MADE)
                parts.append(tmpl.format(
                    shooter=event.shooter_name,
                    zone=event.zone,
                    distance=f"{event.distance:.0f}",
                ))

            # And-one
            if event.is_and_one:
                suffix = self._pick_template(AND_ONE_SUFFIX)
                parts.append(suffix)

            # Score update -- guard against lead=0 (tie game)
            score_diff = event.new_score_home - event.new_score_away
            if score_diff == 0:
                tmpl = self._pick_template(TIE_SCORE_TEMPLATES)
                parts.append(tmpl.format(
                    score=event.new_score_home,
                ))
            elif event.lead and event.lead != 0:
                parts.append(f"{event.team_name} {event.new_score_home}-{event.new_score_away}.")
        else:
            # Missed shot
            if event.is_three:
                tmpl = self._pick_template(THREE_POINTER_MISSED)
            elif event.distance < 8.0:
                tmpl = self._pick_template(CLOSE_RANGE_MISSED)
            else:
                tmpl = self._pick_template(MID_RANGE_MISSED)
            parts.append(tmpl.format(
                shooter=event.shooter_name,
                zone=event.zone,
                distance=f"{event.distance:.0f}",
            ))

        return " ".join(parts)

    def _narrate_rebound(self, event: ReboundEvent) -> Optional[str]:
        if event.is_offensive:
            templates = [
                f"{event.rebounder_name} grabs the offensive board!",
                f"Offensive rebound, {event.rebounder_name}! Second chance!",
                f"{event.rebounder_name} keeps it alive with the offensive rebound!",
            ]
        else:
            templates = [
                f"{event.rebounder_name} grabs the rebound.",
                f"Rebound {event.rebounder_name}.",
                f"{event.rebounder_name} pulls it down.",
                f"{event.rebounder_name} with the board.",
            ]
        return self._pick_template(templates)

    def _narrate_turnover(self, event: TurnoverEvent) -> Optional[str]:
        if event.is_steal:
            tmpl = self._pick_template(STEAL_TEMPLATES)
            return tmpl.format(
                defender=event.stealer_name,
                handler=event.player_name,
            )
        templates = [
            f"{event.player_name} loses the handle. Turnover.",
            f"Turnover by {event.player_name}. {event.team_name} ball.",
            f"{event.player_name} coughs it up. Turnover.",
            f"{event.player_name} stepped out of bounds. Turnover.",
            f"Ball poked away from {event.player_name}!",
            f"{event.player_name} caught with his head down. Turnover.",
            f"Stripped! {event.player_name} loses it.",
            f"{event.player_name} lost his footing. Ball goes the other way.",
            f"Errant pass by {event.player_name}. That's a turnover.",
            f"Offensive foul called on {event.player_name}. Turnover.",
            f"{event.player_name} bobbles it and loses possession.",
        ]
        return self._pick_template(templates)

    def _narrate_block(self, event: BlockEvent) -> Optional[str]:
        tmpl = self._pick_template(BLOCK_TEMPLATES)
        return tmpl.format(
            blocker=event.blocker_name,
            shooter=event.shooter_name,
        )

    def _narrate_foul(self, event: FoulEvent) -> Optional[str]:
        if event.is_foul_trouble:
            return (
                f"Foul on {event.fouler_name}. That's his "
                f"{event.personal_fouls}th. He's in trouble."
            )
        return (
            f"Foul called on {event.fouler_name}. "
            f"{event.victim_name} will shoot {event.free_throws_awarded}."
        )

    def _narrate_free_throw(self, event: FreeThrowEvent) -> Optional[str]:
        if event.made:
            tmpl = self._pick_template(FREE_THROW_MADE_TEMPLATES)
        else:
            tmpl = self._pick_template(FREE_THROW_MISSED_TEMPLATES)
        return tmpl.format(shooter=event.shooter_name)

    def _narrate_substitution(self, event: SubstitutionEvent) -> Optional[str]:
        tmpl = self._pick_template(SUBSTITUTION_TEMPLATES)
        return tmpl.format(
            player_in=event.player_in_name,
            player_out=event.player_out_name,
            team=event.team_name,
        )

    def _narrate_timeout(self, event: TimeoutEvent) -> Optional[str]:
        tmpl = self._pick_template(TIMEOUT_TEMPLATES)
        return tmpl.format(
            team=event.team_name,
            remaining=event.timeouts_remaining,
        )

    def _narrate_quarter(self, event: QuarterBoundaryEvent) -> Optional[str]:
        if event.kind == QuarterEventKind.HALFTIME:
            tmpl = self._pick_template(HALFTIME_TEMPLATES)
        else:
            tmpl = self._pick_template(BETWEEN_QUARTER_TEMPLATES)

        quarter_names = {
            1: "1st quarter", 2: "2nd quarter",
            3: "3rd quarter", 4: "4th quarter",
        }
        q_name = quarter_names.get(event.quarter, f"OT{event.quarter - 4}")
        return tmpl.format(
            quarter=q_name,
            home_team=event.home_team,
            away_team=event.away_team,
            home_score=event.home_score,
            away_score=event.away_score,
        )

    def _narrate_momentum(self, event: MomentumEvent) -> Optional[str]:
        return None  # Handled by color commentary

    # Handler dispatch table
    _HANDLERS = {
        NarrationEventType.POSSESSION_START: _narrate_possession_start,
        NarrationEventType.BALL_ADVANCE: _narrate_ball_advance,
        NarrationEventType.DRIBBLE_MOVE: _narrate_dribble_move,
        NarrationEventType.SCREEN_ACTION: _narrate_screen,
        NarrationEventType.PASS_ACTION: _narrate_pass,
        NarrationEventType.DRIVE: _narrate_drive,
        NarrationEventType.SHOT_RESULT: _narrate_shot_result,
        NarrationEventType.REBOUND: _narrate_rebound,
        NarrationEventType.TURNOVER: _narrate_turnover,
        NarrationEventType.BLOCK: _narrate_block,
        NarrationEventType.FOUL: _narrate_foul,
        NarrationEventType.FREE_THROW: _narrate_free_throw,
        NarrationEventType.SUBSTITUTION: _narrate_substitution,
        NarrationEventType.TIMEOUT: _narrate_timeout,
        NarrationEventType.QUARTER_EVENT: _narrate_quarter,
        NarrationEventType.MOMENTUM: _narrate_momentum,
    }
