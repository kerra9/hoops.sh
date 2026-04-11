"""Chain composer: weaves event sequences into flowing prose.

Instead of rendering each event as an independent sentence, the
ChainComposer groups consecutive related events into 'action clusters'
and renders each cluster as a clause joined by commas, ellipses, or
dashes -- producing output like real broadcast play-by-play.

Example output:
  "Mitchell hesi... crossover... gets a step! Attacks left, into the
   paint, draws the help from Johnson, kicks it out to Thompson in
   the corner... Thompson catches and fires -- three-ball... BANG!"
"""

from __future__ import annotations

from typing import List, Optional

from hoops_sim.narration.events import (
    BaseNarrationEvent,
    BallAdvanceEvent,
    DribbleMoveEvent,
    DriveEvent,
    NarrationEventType,
    PassEvent,
    ScreenEvent,
)
from hoops_sim.narration.templates.fragments import (
    CATCH_AND_SHOOT_FRAGMENTS,
    DRIBBLE_FRAGMENTS,
    DRIBBLE_FRAGMENTS_GENERIC,
    DRIVE_FRAGMENTS,
    PASS_FRAGMENTS,
    PROBING_FRAGMENTS,
    SCREEN_SETUP_FRAGMENTS,
    SEPARATION_CONNECTORS,
    TRANSITION_CONNECTORS,
)
from hoops_sim.utils.rng import SeededRNG


class ActionCluster:
    """A group of consecutive related events rendered as one clause."""

    def __init__(self, cluster_type: str) -> None:
        self.cluster_type = cluster_type
        self.events: List[BaseNarrationEvent] = []

    def add(self, event: BaseNarrationEvent) -> None:
        self.events.append(event)

    @property
    def is_empty(self) -> bool:
        return len(self.events) == 0


class ChainComposer:
    """Weaves a sequence of narration events into flowing prose.

    Groups consecutive events into action clusters, then renders each
    cluster as clauses joined by connectors instead of isolated sentences.
    """

    def __init__(self, rng: SeededRNG) -> None:
        self.rng = rng
        self._recent_fragments: List[str] = []
        self._max_recent = 15

    def compose(
        self,
        events: List[BaseNarrationEvent],
        verbosity: float = 0.5,
    ) -> str:
        """Compose a sequence of setup events into flowing prose.

        Args:
            events: Ordered list of setup events for the possession.
            verbosity: 0.0-1.0 controlling how much detail to include.

        Returns:
            A flowing paragraph of play-by-play text.
        """
        if not events:
            return ""

        clusters = self._group_into_clusters(events)
        rendered = self._render_clusters(clusters, verbosity)
        return rendered

    def _group_into_clusters(
        self, events: List[BaseNarrationEvent],
    ) -> List[ActionCluster]:
        """Group consecutive related events into action clusters."""
        clusters: List[ActionCluster] = []
        current: Optional[ActionCluster] = None

        for event in events:
            cluster_type = self._event_cluster_type(event)

            if current is None:
                current = ActionCluster(cluster_type)
                current.add(event)
            elif self._should_merge(current, event, cluster_type):
                current.add(event)
            else:
                clusters.append(current)
                current = ActionCluster(cluster_type)
                current.add(event)

        if current and not current.is_empty:
            clusters.append(current)

        return clusters

    def _event_cluster_type(self, event: BaseNarrationEvent) -> str:
        """Map an event to its cluster type."""
        mapping = {
            NarrationEventType.DRIBBLE_MOVE: "dribble",
            NarrationEventType.DRIVE: "drive",
            NarrationEventType.SCREEN_ACTION: "screen",
            NarrationEventType.PASS_ACTION: "pass",
            NarrationEventType.BALL_ADVANCE: "advance",
            NarrationEventType.OFF_BALL_ACTION: "offball",
            NarrationEventType.DEFENSIVE_ACTION: "defense",
        }
        return mapping.get(event.event_type, "other")

    def _should_merge(
        self,
        current: ActionCluster,
        event: BaseNarrationEvent,
        cluster_type: str,
    ) -> bool:
        """Decide whether to merge an event into the current cluster."""
        # Same type clusters merge (e.g. dribble combo)
        if current.cluster_type == cluster_type:
            return True
        # Drive merges with preceding dribble (dribble-into-drive)
        if current.cluster_type == "dribble" and cluster_type == "drive":
            return True
        # Pass chains merge
        if current.cluster_type == "pass" and cluster_type == "pass":
            return True
        return False

    def _render_clusters(
        self,
        clusters: List[ActionCluster],
        verbosity: float,
    ) -> str:
        """Render a list of clusters into flowing prose."""
        parts: List[str] = []

        for i, cluster in enumerate(clusters):
            rendered = self._render_cluster(cluster, verbosity)
            if not rendered:
                continue

            if i == 0:
                parts.append(rendered)
            else:
                # Join clusters with transitional connectors
                connector = self._pick_fragment(TRANSITION_CONNECTORS)
                # Use ellipsis between major action changes
                if clusters[i - 1].cluster_type != cluster.cluster_type:
                    parts.append(f"... {rendered}")
                else:
                    parts.append(f", {connector} {rendered}")

        return "".join(parts)

    def _render_cluster(
        self,
        cluster: ActionCluster,
        verbosity: float,
    ) -> str:
        """Render a single action cluster as a clause."""
        if cluster.cluster_type == "dribble":
            return self._render_dribble_cluster(cluster, verbosity)
        if cluster.cluster_type == "drive":
            return self._render_drive_cluster(cluster, verbosity)
        if cluster.cluster_type == "screen":
            return self._render_screen_cluster(cluster)
        if cluster.cluster_type == "pass":
            return self._render_pass_cluster(cluster)
        if cluster.cluster_type == "advance":
            return self._render_advance_cluster(cluster, verbosity)
        # Default: just use the first event's basic description
        return ""

    def _render_dribble_cluster(
        self,
        cluster: ActionCluster,
        verbosity: float,
    ) -> str:
        """Render a dribble combo as flowing fragments.

        For combos of 2+ moves, joins fragments with ellipses:
        'hesi... crossover... behind the back, creates space!'

        For a single dribble, renders a short fragment with the player name.
        """
        dribble_events = [
            e for e in cluster.events
            if isinstance(e, DribbleMoveEvent)
        ]
        drive_events = [
            e for e in cluster.events
            if isinstance(e, DriveEvent)
        ]

        if not dribble_events:
            return ""

        first = dribble_events[0]
        player_name = first.player_name

        if len(dribble_events) == 1 and not drive_events:
            # Single dribble move -- include player name
            frag = self._dribble_fragment(first.move_type)
            return f"{player_name} {frag}"

        # Multi-move combo
        fragments: List[str] = []
        for i, de in enumerate(dribble_events):
            frag = self._dribble_fragment(de.move_type)
            if i == 0:
                fragments.append(f"{player_name} {frag}")
            else:
                fragments.append(frag)

            # At high verbosity, maybe add a separation connector
            if (
                verbosity > 0.6
                and i < len(dribble_events) - 1
                and de.success
                and de.separation_gained > 0.5
            ):
                conn = self._pick_fragment(SEPARATION_CONNECTORS)
                fragments.append(conn)

        # If there's a drive at the end, append it
        if drive_events:
            drive_frag = self._pick_fragment(DRIVE_FRAGMENTS)
            fragments.append(drive_frag)

        return "... ".join(fragments)

    def _render_drive_cluster(
        self,
        cluster: ActionCluster,
        verbosity: float,
    ) -> str:
        """Render a drive action."""
        drive_events = [
            e for e in cluster.events if isinstance(e, DriveEvent)
        ]
        if not drive_events:
            return ""

        de = drive_events[0]
        frag = self._pick_fragment(DRIVE_FRAGMENTS)
        result = f"{de.driver_name} {frag}"

        if de.kick_out and de.kick_out_target:
            result += f", kicks it out to {de.kick_out_target}"

        return result

    def _render_screen_cluster(self, cluster: ActionCluster) -> str:
        """Render a screen action."""
        screen_events = [
            e for e in cluster.events if isinstance(e, ScreenEvent)
        ]
        if not screen_events:
            return ""

        se = screen_events[0]
        setup = self._pick_fragment(SCREEN_SETUP_FRAGMENTS)
        result = f"{se.handler_name} {setup} from {se.screener_name}"

        return result

    def _render_pass_cluster(self, cluster: ActionCluster) -> str:
        """Render a pass chain."""
        pass_events = [
            e for e in cluster.events if isinstance(e, PassEvent)
        ]
        if not pass_events:
            return ""

        parts: List[str] = []
        for pe in pass_events:
            frag_templates = PASS_FRAGMENTS
            frag = self._pick_fragment(frag_templates)
            try:
                rendered = frag.format(receiver=pe.receiver_name)
            except (KeyError, IndexError):
                rendered = f"finds {pe.receiver_name}"
            if not parts:
                parts.append(f"{pe.passer_name} {rendered}")
            else:
                parts.append(rendered)

        return ", ".join(parts)

    def _render_advance_cluster(
        self,
        cluster: ActionCluster,
        verbosity: float,
    ) -> str:
        """Render ball advance. Only at medium+ verbosity."""
        if verbosity < 0.3:
            return ""

        advance_events = [
            e for e in cluster.events if isinstance(e, BallAdvanceEvent)
        ]
        if not advance_events:
            return ""

        ae = advance_events[0]
        if ae.is_transition:
            return f"{ae.ball_handler_name} pushes it ahead in transition"

        probing = self._pick_fragment(PROBING_FRAGMENTS)
        return f"{ae.ball_handler_name} brings it up, {probing}"

    def _dribble_fragment(self, move_type: str) -> str:
        """Pick a dribble fragment for the given move type."""
        frags = DRIBBLE_FRAGMENTS.get(move_type, DRIBBLE_FRAGMENTS_GENERIC)
        return self._pick_fragment(frags)

    def _pick_fragment(self, options: List[str]) -> str:
        """Select a fragment, avoiding recent repeats."""
        available = [f for f in options if f not in self._recent_fragments]
        if not available:
            available = options
        choice = self.rng.choice(available)
        self._recent_fragments.append(choice)
        if len(self._recent_fragments) > self._max_recent:
            self._recent_fragments.pop(0)
        return choice
