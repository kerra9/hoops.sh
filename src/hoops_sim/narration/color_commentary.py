"""Color commentary narrator: the analyst voice.

Provides tactical analysis, statistical context, matchup insight,
fatigue commentary, and game narrative observations. Interjects
between possessions or during dead balls.
"""

from __future__ import annotations

from typing import List, Optional

from hoops_sim.narration.events import (
    BaseNarrationEvent,
    FoulEvent,
    MomentumEvent,
    MomentumKind,
    NarrationEventType,
    ShotResultEvent,
    SubstitutionEvent,
    TimeoutEvent,
    TurnoverEvent,
)
from hoops_sim.narration.narrative_arc import ArcSnapshot, ArcType, NarrativeArcTracker
from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.narration.templates.color import (
    BLOWOUT_TEMPLATES,
    COLD_PLAYER_TEMPLATES,
    COMEBACK_TEMPLATES,
    DEFENSIVE_SCHEME_TEMPLATES,
    FATIGUE_TEMPLATES,
    FOUL_TROUBLE_TEMPLATES,
    HOT_PLAYER_TEMPLATES,
    STAT_INSIGHT_TEMPLATES,
    TIMEOUT_ANALYSIS,
)
from hoops_sim.narration.templates.context_suffixes import (
    CLUTCH_TEMPLATES,
    COLD_STREAK_TEMPLATES,
    DROUGHT_TEMPLATES,
    HOT_STREAK_TEMPLATES,
    LEAD_CHANGE_TEMPLATES,
    MILESTONE_TEMPLATES,
    SCORING_RUN_TEMPLATES,
    SHOOTING_LINE_TEMPLATES,
    TIE_GAME_TEMPLATES,
    ordinal,
)
from hoops_sim.utils.rng import SeededRNG


class ColorCommentaryNarrator:
    """Generates analyst-style color commentary.

    Interjects with context, analysis, and insight based on the
    game state, statistical trends, and narrative arcs.
    """

    def __init__(
        self,
        rng: SeededRNG,
        stat_tracker: LiveStatTracker,
        arc_tracker: NarrativeArcTracker,
    ) -> None:
        self.rng = rng
        self.stats = stat_tracker
        self.arcs = arc_tracker
        self._cooldown = 0  # possessions since last commentary
        self._recent_templates: List[str] = []
        self._max_recent = 8

    def _pick_template(self, templates: List[str]) -> str:
        """Select a template, avoiding recent repeats."""
        available = [t for t in templates if t not in self._recent_templates]
        if not available:
            available = templates
        choice = self.rng.choice(available)
        self._recent_templates.append(choice)
        if len(self._recent_templates) > self._max_recent:
            self._recent_templates.pop(0)
        return choice

    def should_interject(self, event: BaseNarrationEvent) -> bool:
        """Decide whether to add color commentary for this event."""
        # Always comment on timeouts, quarter events, big plays
        if event.event_type in (
            NarrationEventType.TIMEOUT,
            NarrationEventType.QUARTER_EVENT,
            NarrationEventType.MOMENTUM,
        ):
            return True

        # Comment on made shots with context
        if event.event_type == NarrationEventType.SHOT_RESULT:
            shot = event  # type: ignore[assignment]
            if isinstance(shot, ShotResultEvent):
                if shot.made:
                    pstats = self.stats.get_player(shot.shooter_id, shot.shooter_name)
                    # Comment if player is hot, hit milestone, or it's a big play
                    if pstats.is_hot or pstats.next_milestone or pstats.points >= 25:
                        return True

        # Comment on foul trouble
        if event.event_type == NarrationEventType.FOUL:
            if isinstance(event, FoulEvent) and event.is_foul_trouble:
                return True

        # Cooldown-based: comment roughly every 3-5 possessions
        if self._cooldown >= 3 and self.rng.random() < 0.5:
            self._cooldown = 0
            return True

        return False

    def generate(
        self,
        event: BaseNarrationEvent,
        arc_snapshot: ArcSnapshot,
    ) -> Optional[str]:
        """Generate color commentary text for the given event and game state."""
        self._cooldown += 1
        parts: List[str] = []

        # Event-specific commentary
        event_comment = self._event_commentary(event)
        if event_comment:
            parts.append(event_comment)

        # Arc-based commentary (if the arc is strong enough)
        if arc_snapshot.has_active_arc:
            arc = arc_snapshot.primary_arc
            assert arc is not None
            arc_comment = self._arc_commentary(arc.arc_type, arc.team_or_player, arc.intensity)
            if arc_comment and self.rng.random() < arc.intensity * 0.6:
                parts.append(arc_comment)

        if not parts:
            return None

        return " ".join(parts)

    def _event_commentary(self, event: BaseNarrationEvent) -> Optional[str]:
        """Generate commentary specific to an event type."""
        if isinstance(event, ShotResultEvent) and event.made:
            return self._shot_context(event)
        if isinstance(event, TimeoutEvent):
            return self._timeout_context(event)
        if isinstance(event, FoulEvent) and event.is_foul_trouble:
            return self._foul_context(event)
        if isinstance(event, MomentumEvent):
            return self._momentum_context(event)
        return None

    def _shot_context(self, event: ShotResultEvent) -> Optional[str]:
        """Provide context after a made shot."""
        pstats = self.stats.get_player(event.shooter_id, event.shooter_name)

        # Hot streak
        if pstats.consecutive_makes >= 4:
            tmpl = self._pick_template(HOT_PLAYER_TEMPLATES)
            return tmpl.format(player=event.shooter_name)

        # Shooting line
        if pstats.fg_attempted >= 5:
            tmpl = self._pick_template(SHOOTING_LINE_TEMPLATES)
            return tmpl.format(
                player=event.shooter_name,
                made=pstats.fg_made,
                attempted=pstats.fg_attempted,
            )

        # Milestone
        if pstats.points >= 20:
            tmpl = self._pick_template(MILESTONE_TEMPLATES)
            return tmpl.format(
                player=event.shooter_name,
                points=pstats.points,
            )

        return None

    def _timeout_context(self, event: TimeoutEvent) -> Optional[str]:
        tmpl = self._pick_template(TIMEOUT_ANALYSIS)
        return tmpl

    def _foul_context(self, event: FoulEvent) -> Optional[str]:
        tmpl = self._pick_template(FOUL_TROUBLE_TEMPLATES)
        return tmpl.format(
            player=event.fouler_name,
            fouls=event.personal_fouls,
        )

    def _momentum_context(self, event: MomentumEvent) -> Optional[str]:
        if event.kind == MomentumKind.RUN_EXTENDED:
            tmpl = self._pick_template(SCORING_RUN_TEMPLATES)
            return tmpl.format(
                team=event.team_name,
                points=event.run_points,
                against=0,
                total=event.run_points,
            )
        if event.kind == MomentumKind.LEAD_CHANGE:
            tmpl = self._pick_template(LEAD_CHANGE_TEMPLATES)
            return tmpl.format(
                team=event.team_name,
                lead="",
                quarter="",
            )
        if event.kind == MomentumKind.TIE_GAME:
            tmpl = self._pick_template(TIE_GAME_TEMPLATES)
            return tmpl
        return None

    def _arc_commentary(
        self, arc_type: ArcType, subject: str, intensity: float,
    ) -> Optional[str]:
        """Generate commentary based on the current narrative arc."""
        if arc_type == ArcType.COMEBACK:
            tmpl = self._pick_template(COMEBACK_TEMPLATES)
            return tmpl.format(
                from_lead="big", to_lead="small",
                team=subject,
            )
        if arc_type == ArcType.BLOWOUT:
            tmpl = self._pick_template(BLOWOUT_TEMPLATES)
            return tmpl.format(team=subject)
        if arc_type == ArcType.STAR_PERFORMANCE:
            tmpl = self._pick_template(HOT_PLAYER_TEMPLATES)
            return tmpl.format(player=subject)
        if arc_type == ArcType.FOUL_TROUBLE:
            tmpl = self._pick_template(FOUL_TROUBLE_TEMPLATES)
            return tmpl.format(player=subject, fouls="multiple")
        if arc_type == ArcType.CLOSE_GAME:
            tmpl = self._pick_template(CLUTCH_TEMPLATES)
            return tmpl.format(player=subject)
        return None
