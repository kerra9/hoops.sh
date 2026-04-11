"""Topic-driven analyst voice for color commentary.

Replaces the old cooldown-based system with a topic-driven approach
where the analyst always has something relevant to say: matchup
analysis, scheme commentary, tendency awareness, fatigue reads,
adjustment tracking, and statistical context.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set

from hoops_sim.narration.events import (
    BaseNarrationEvent,
    MomentumEvent,
    MomentumKind,
    NarrationEventType,
    ScreenEvent,
    ShotResultEvent,
    TurnoverEvent,
    TimeoutEvent,
    FoulEvent,
)
from hoops_sim.narration.narrative_arc import ArcSnapshot, ArcType
from hoops_sim.narration.stat_tracker import LiveStatTracker
from hoops_sim.narration.templates.color import (
    BLOWOUT_TEMPLATES,
    COLD_PLAYER_TEMPLATES,
    COMEBACK_TEMPLATES,
    DEFENSIVE_SCHEME_TEMPLATES,
    FATIGUE_TEMPLATES,
    FOUL_TROUBLE_TEMPLATES,
    HOT_PLAYER_TEMPLATES,
    MISMATCH_TEMPLATES,
    PNR_COVERAGE_ANALYSIS,
    STAT_INSIGHT_TEMPLATES,
    TENDENCY_TEMPLATES,
    TIMEOUT_ANALYSIS,
)
from hoops_sim.narration.templates.context_suffixes import (
    CLUTCH_TEMPLATES,
    LEAD_CHANGE_TEMPLATES,
    MILESTONE_TEMPLATES,
    SCORING_RUN_TEMPLATES,
    SHOOTING_LINE_TEMPLATES,
    TIE_GAME_TEMPLATES,
)
from hoops_sim.utils.rng import SeededRNG


class AnalystTopic:
    """A topic the analyst can speak about."""

    def __init__(self, name: str, relevance: float, text: str) -> None:
        self.name = name
        self.relevance = relevance  # 0.0 to 1.0
        self.text = text


class AnalystVoice:
    """Topic-driven analyst providing tactical insight and context.

    The analyst interjects after made shots, turnovers, timeouts, and
    during dead balls. Uses past tense, analytical language, and
    references 'you' and 'they' -- distinct from the PBP voice.
    """

    def __init__(
        self,
        rng: SeededRNG,
        stat_tracker: LiveStatTracker,
    ) -> None:
        self.rng = rng
        self.stats = stat_tracker
        self._recent_topics: List[str] = []
        self._max_recent_topics = 5
        self._recent_templates: List[str] = []
        self._max_recent = 8
        self._pnr_coverage_seen: Dict[str, int] = {}
        self._scheme_changes: List[str] = []

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
        """Decide whether the analyst should speak after this event."""
        # Always after timeouts, quarter events, momentum shifts
        if event.event_type in (
            NarrationEventType.TIMEOUT,
            NarrationEventType.QUARTER_EVENT,
            NarrationEventType.MOMENTUM,
        ):
            return True

        # After made shots -- stat line, shooting context
        if isinstance(event, ShotResultEvent) and event.made:
            pstats = self.stats.get_player(event.shooter_id, event.shooter_name)
            if pstats.is_hot or pstats.points >= 20 or pstats.next_milestone:
                return True
            # Interject on 30-50% of other makes
            return self.rng.random() < 0.35

        # After turnovers -- tactical analysis
        if isinstance(event, TurnoverEvent):
            return self.rng.random() < 0.4

        # Foul trouble
        if isinstance(event, FoulEvent) and event.is_foul_trouble:
            return True

        # Screen events -- scheme commentary
        if isinstance(event, ScreenEvent) and event.pnr_coverage:
            return self.rng.random() < 0.25

        return False

    def generate(
        self,
        event: BaseNarrationEvent,
        arc_snapshot: ArcSnapshot,
    ) -> Optional[str]:
        """Generate analyst commentary for the event and game state.

        Builds a list of candidate topics, picks the most relevant
        one that hasn't been used recently, and formats it.
        """
        topics = self._gather_topics(event, arc_snapshot)

        # Filter out recently discussed topics
        available = [
            t for t in topics
            if t.name not in self._recent_topics
        ]
        if not available:
            available = topics

        if not available:
            return None

        # Pick the most relevant topic
        available.sort(key=lambda t: t.relevance, reverse=True)
        chosen = available[0]

        self._recent_topics.append(chosen.name)
        if len(self._recent_topics) > self._max_recent_topics:
            self._recent_topics.pop(0)

        return chosen.text

    def _gather_topics(
        self,
        event: BaseNarrationEvent,
        arc_snapshot: ArcSnapshot,
    ) -> List[AnalystTopic]:
        """Build candidate topics for commentary."""
        topics: List[AnalystTopic] = []

        # Event-specific topics
        if isinstance(event, ShotResultEvent) and event.made:
            topics.extend(self._shot_topics(event))
        elif isinstance(event, TurnoverEvent):
            topics.extend(self._turnover_topics(event))
        elif isinstance(event, TimeoutEvent):
            topics.extend(self._timeout_topics(event))
        elif isinstance(event, FoulEvent) and event.is_foul_trouble:
            topics.extend(self._foul_topics(event))
        elif isinstance(event, MomentumEvent):
            topics.extend(self._momentum_topics(event))
        elif isinstance(event, ScreenEvent):
            topics.extend(self._scheme_topics(event))

        # Arc-based topics
        if arc_snapshot.has_active_arc and arc_snapshot.primary_arc:
            arc = arc_snapshot.primary_arc
            arc_topic = self._arc_topic(arc.arc_type, arc.team_or_player, arc.intensity)
            if arc_topic:
                topics.append(arc_topic)

        return topics

    def _shot_topics(self, event: ShotResultEvent) -> List[AnalystTopic]:
        """Generate topics after a made shot."""
        topics: List[AnalystTopic] = []
        pstats = self.stats.get_player(event.shooter_id, event.shooter_name)

        # Shooting line
        if pstats.fg_attempted >= 5:
            tmpl = self._pick_template(SHOOTING_LINE_TEMPLATES)
            text = tmpl.format(
                player=event.shooter_name,
                made=pstats.fg_made,
                attempted=pstats.fg_attempted,
            )
            topics.append(AnalystTopic("shooting_line", 0.6, text))

        # Hot streak
        if pstats.consecutive_makes >= 3:
            tmpl = self._pick_template(HOT_PLAYER_TEMPLATES)
            text = tmpl.format(player=event.shooter_name)
            topics.append(AnalystTopic("hot_streak", 0.8, text))

        # Milestone
        if pstats.points >= 20:
            tmpl = self._pick_template(MILESTONE_TEMPLATES)
            text = tmpl.format(
                player=event.shooter_name,
                points=pstats.points,
            )
            topics.append(AnalystTopic("milestone", 0.7, text))

        # Three-point shooting context
        if event.is_three and pstats.three_attempted >= 3:
            text = (
                f"That's {pstats.three_made}-for-{pstats.three_attempted} "
                f"from deep tonight for {event.shooter_name}."
            )
            topics.append(AnalystTopic("three_pt_line", 0.65, text))

        return topics

    def _turnover_topics(self, event: TurnoverEvent) -> List[AnalystTopic]:
        """Generate topics after a turnover."""
        topics: List[AnalystTopic] = []
        pstats = self.stats.get_player(event.player_id, event.player_name)

        if pstats.turnovers >= 3:
            text = (
                f"That's {pstats.turnovers} turnovers now for "
                f"{event.player_name}. That's been a problem tonight."
            )
            topics.append(AnalystTopic("turnover_count", 0.7, text))

        if event.is_steal:
            text = (
                f"Great read by {event.stealer_name}. "
                f"That kind of defense changes possessions."
            )
            topics.append(AnalystTopic("steal_analysis", 0.6, text))

        return topics

    def _timeout_topics(self, event: TimeoutEvent) -> List[AnalystTopic]:
        """Generate topics during a timeout."""
        topics: List[AnalystTopic] = []

        tmpl = self._pick_template(TIMEOUT_ANALYSIS)
        topics.append(AnalystTopic("timeout_analysis", 0.8, tmpl))

        if event.opponent_run and event.opponent_run >= 7:
            text = (
                f"Had to stop that run. They've given up "
                f"{event.opponent_run} unanswered."
            )
            topics.append(AnalystTopic("timeout_run", 0.9, text))

        return topics

    def _foul_topics(self, event: FoulEvent) -> List[AnalystTopic]:
        """Generate topics on foul trouble."""
        tmpl = self._pick_template(FOUL_TROUBLE_TEMPLATES)
        text = tmpl.format(
            player=event.fouler_name,
            fouls=event.personal_fouls,
        )
        return [AnalystTopic("foul_trouble", 0.85, text)]

    def _momentum_topics(self, event: MomentumEvent) -> List[AnalystTopic]:
        """Generate topics on momentum shifts."""
        topics: List[AnalystTopic] = []

        if event.kind == MomentumKind.RUN_EXTENDED:
            tmpl = self._pick_template(SCORING_RUN_TEMPLATES)
            text = tmpl.format(
                team=event.team_name,
                points=event.run_points,
                against=0,
                total=event.run_points,
            )
            topics.append(AnalystTopic("scoring_run", 0.8, text))

        if event.kind == MomentumKind.LEAD_CHANGE:
            tmpl = self._pick_template(LEAD_CHANGE_TEMPLATES)
            text = tmpl.format(
                team=event.team_name, lead="", quarter="",
            )
            topics.append(AnalystTopic("lead_change", 0.7, text))

        if event.kind == MomentumKind.TIE_GAME:
            tmpl = self._pick_template(TIE_GAME_TEMPLATES)
            topics.append(AnalystTopic("tie_game", 0.7, tmpl))

        return topics

    def _scheme_topics(self, event: ScreenEvent) -> List[AnalystTopic]:
        """Generate PnR coverage analysis."""
        if not event.pnr_coverage:
            return []

        # Track coverage patterns
        coverage = event.pnr_coverage
        self._pnr_coverage_seen[coverage] = (
            self._pnr_coverage_seen.get(coverage, 0) + 1
        )

        tmpl = self._pick_template(PNR_COVERAGE_ANALYSIS)
        return [AnalystTopic("pnr_scheme", 0.5, tmpl)]

    def _arc_topic(
        self,
        arc_type: ArcType,
        subject: str,
        intensity: float,
    ) -> Optional[AnalystTopic]:
        """Generate a topic from the current narrative arc."""
        if arc_type == ArcType.COMEBACK:
            tmpl = self._pick_template(COMEBACK_TEMPLATES)
            text = tmpl.format(
                from_lead="big", to_lead="small", team=subject,
            )
            return AnalystTopic("comeback_arc", intensity, text)

        if arc_type == ArcType.BLOWOUT:
            tmpl = self._pick_template(BLOWOUT_TEMPLATES)
            text = tmpl.format(team=subject)
            return AnalystTopic("blowout_arc", intensity * 0.6, text)

        if arc_type == ArcType.STAR_PERFORMANCE:
            tmpl = self._pick_template(HOT_PLAYER_TEMPLATES)
            text = tmpl.format(player=subject)
            return AnalystTopic("star_arc", intensity, text)

        if arc_type == ArcType.CLOSE_GAME:
            tmpl = self._pick_template(CLUTCH_TEMPLATES)
            text = tmpl.format(player=subject)
            return AnalystTopic("close_game_arc", intensity, text)

        return None

    def track_pnr_coverage(self, coverage: str) -> None:
        """Record a PnR coverage observation for trend tracking."""
        self._pnr_coverage_seen[coverage] = (
            self._pnr_coverage_seen.get(coverage, 0) + 1
        )
