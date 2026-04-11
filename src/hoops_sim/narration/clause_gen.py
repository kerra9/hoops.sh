"""Layer 4: Clause Generation.

Converts each dramatic beat into one or more narrative clauses --
the atomic units of prose. Dispatches to clause banks based on
event type and intensity band.
"""

from __future__ import annotations

from hoops_sim.narration.clause_banks import intensity_band
from hoops_sim.narration.clause_banks.defense import get_block_clauses, get_defender_clauses
from hoops_sim.narration.clause_banks.dribble import get_dribble_clauses
from hoops_sim.narration.clause_banks.drive import get_drive_clauses
from hoops_sim.narration.clause_banks.pass_ import get_pass_clauses
from hoops_sim.narration.clause_banks.reaction import (
    get_announcer_reactions,
    get_crowd_reactions,
    get_separation_clauses,
    get_staredown_clauses,
)
from hoops_sim.narration.clause_banks.screen import get_screen_clauses
from hoops_sim.narration.clause_banks.setup import get_setup_clauses
from hoops_sim.narration.clause_banks.shot import get_shot_clauses
from hoops_sim.narration.events import (
    BallAdvanceEvent,
    BlockEvent,
    DribbleMoveEvent,
    DriveEvent,
    FoulEvent,
    FreeThrowEvent,
    MomentumEvent,
    NarrationEventType,
    PassEvent,
    ProbingEvent,
    ReboundEvent,
    ScreenEvent,
    ShotAttemptEvent,
    ShotResultEvent,
    TurnoverEvent,
)
from hoops_sim.narration.types import Clause, DramaticBeat, DramaticPlan, DramaticRole
from hoops_sim.utils.rng import SeededRNG


class DefaultClauseGenerator:
    """Default implementation of the ClauseGenerator protocol.

    Dispatches to registered bank-based generators per event type.
    Each beat produces one or more clauses depending on event type
    and intensity level.
    """

    def generate(
        self, beat: DramaticBeat, plan: DramaticPlan, rng: SeededRNG,
    ) -> list[Clause]:
        """Generate clauses for a single dramatic beat."""
        event = beat.event
        raw = event.raw
        band = intensity_band(beat.intensity)

        etype = raw.event_type
        handler = _GENERATORS.get(etype, _generate_generic)
        return handler(beat, band, rng)


# ---------------------------------------------------------------------------
# Per-event-type generators
# ---------------------------------------------------------------------------


def _pick(rng: SeededRNG, options: list[str]) -> str:
    """Safely pick from a list, falling back to first element."""
    if not options:
        return ""
    return rng.choice(options)


def _fill_template(text: str, beat: DramaticBeat) -> str:
    """Replace template variables with actual values."""
    ev = beat.event
    result = text
    result = result.replace("{defender}", ev.defender_name or "the defender")
    result = result.replace("{DEFENDER}", (ev.defender_name or "THE DEFENDER").upper())
    result = result.replace("{zone}", ev.spatial or "the floor")
    result = result.replace("{ZONE}", (ev.spatial or "THE FLOOR").upper())

    # Handle receiver for pass events
    raw = ev.raw
    if isinstance(raw, PassEvent):
        result = result.replace("{receiver}", raw.receiver_name or "the open man")
        result = result.replace("{RECEIVER}", (raw.receiver_name or "THE OPEN MAN").upper())
    if isinstance(raw, BlockEvent):
        result = result.replace("{blocker}", raw.blocker_name or "the defender")
        result = result.replace("{BLOCKER}", (raw.blocker_name or "THE DEFENDER").upper())

    return result


def _generate_ball_advance(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for ball advance events."""
    raw = beat.event.raw
    setup_type = "walk_it_up"
    if isinstance(raw, BallAdvanceEvent) and raw.is_transition:
        setup_type = "transition"

    options = get_setup_clauses(setup_type, band)
    text = _fill_template(_pick(rng, options), beat)

    return [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="ball_advance",
        tags={"setup", "ball_advance"},
    )]


def _generate_dribble_move(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for dribble move events."""
    raw = beat.event.raw
    move_type = "crossover"
    if isinstance(raw, DribbleMoveEvent):
        move_type = raw.move_type or "crossover"

    options = get_dribble_clauses(move_type, band)
    text = _fill_template(_pick(rng, options), beat)
    clauses = [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="dribble_move",
        tags={"dribble", move_type},
    )]

    # Multi-clause generation for ankle breakers at high intensity
    if isinstance(raw, DribbleMoveEvent) and raw.ankle_breaker and beat.intensity >= 0.6:
        # Add defender clause
        if beat.event.defender_name:
            defender_opts = get_defender_clauses(beat.defender_dignity)
            def_text = _fill_template(_pick(rng, defender_opts), beat)
            clauses.append(Clause(
                text=def_text,
                subject=beat.event.defender_name,
                subject_type="defender",
                intensity=beat.intensity,
                role=beat.role,
                is_defender_clause=True,
                source_event_type="dribble_move",
                tags={"defender", "ankle_breaker"},
            ))

        # Add separation clause at very high intensity
        if beat.intensity >= 0.75:
            sep_opts = get_separation_clauses(band)
            sep_text = _fill_template(_pick(rng, sep_opts), beat)
            clauses.append(Clause(
                text=sep_text,
                subject=None,
                subject_type="announcer",
                intensity=beat.intensity,
                role=beat.role,
                is_reaction=True,
                source_event_type="dribble_move",
                tags={"reaction", "separation"},
            ))

    return clauses


def _generate_screen(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for screen action events."""
    raw = beat.event.raw
    screen_type = "screen_set"
    if isinstance(raw, ScreenEvent) and raw.switch_occurred:
        screen_type = "switch"

    options = get_screen_clauses(screen_type, band)
    text = _fill_template(_pick(rng, options), beat)

    return [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="screen_action",
        tags={"screen", screen_type},
    )]


def _generate_pass(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for pass events."""
    options = get_pass_clauses(band)
    text = _fill_template(_pick(rng, options), beat)

    return [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="pass_action",
        tags={"pass"},
    )]


def _generate_drive(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for drive events."""
    options = get_drive_clauses(band)
    text = _fill_template(_pick(rng, options), beat)
    clauses = [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="drive",
        tags={"drive"},
    )]

    # Add defender clause if dignity is low and intensity is high
    if beat.defender_dignity < 0.6 and beat.intensity >= 0.5 and beat.event.defender_name:
        defender_opts = get_defender_clauses(beat.defender_dignity)
        def_text = _fill_template(_pick(rng, defender_opts), beat)
        clauses.append(Clause(
            text=def_text,
            subject=beat.event.defender_name,
            subject_type="defender",
            intensity=beat.intensity,
            role=beat.role,
            is_defender_clause=True,
            source_event_type="drive",
            tags={"defender", "drive_defense"},
        ))

    return clauses


def _generate_shot_result(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for shot result events."""
    raw = beat.event.raw
    made = False
    is_three = False
    is_dunk = False

    if isinstance(raw, ShotResultEvent):
        made = raw.made
        is_three = raw.is_three
        is_dunk = raw.is_dunk

    options = get_shot_clauses(made, is_three, is_dunk, band)
    text = _fill_template(_pick(rng, options), beat)
    clauses = [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="shot_result",
        tags={"shot", "made" if made else "missed"},
    )]

    # Add announcer reaction for high-intensity makes
    if made and beat.intensity >= 0.7:
        reaction_opts = get_announcer_reactions(band)
        reaction_text = _pick(rng, reaction_opts)
        clauses.append(Clause(
            text=reaction_text,
            subject=None,
            subject_type="announcer",
            intensity=beat.intensity,
            role=DramaticRole.AFTERMATH,
            is_reaction=True,
            source_event_type="shot_result",
            tags={"reaction", "announcer"},
        ))

    # Add staredown for very high intensity ankle-breaker-to-make sequences
    if made and beat.intensity >= 0.85 and beat.event.defender_name:
        staredown_opts = get_staredown_clauses(band)
        stare_text = _fill_template(_pick(rng, staredown_opts), beat)
        clauses.append(Clause(
            text=stare_text,
            subject=beat.event.player_name,
            subject_type="handler",
            intensity=beat.intensity,
            role=DramaticRole.AFTERMATH,
            source_event_type="shot_result",
            tags={"staredown", "aftermath"},
        ))

    return clauses


def _generate_block(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for block events."""
    options = get_block_clauses(band)
    text = _fill_template(_pick(rng, options), beat)

    clauses = [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="block",
        tags={"block", "defense"},
    )]

    # Announcer reaction for big blocks
    if beat.intensity >= 0.7:
        reaction_opts = get_announcer_reactions(band)
        clauses.append(Clause(
            text=_pick(rng, reaction_opts),
            subject=None,
            subject_type="announcer",
            intensity=beat.intensity,
            role=DramaticRole.AFTERMATH,
            is_reaction=True,
            source_event_type="block",
            tags={"reaction", "block_reaction"},
        ))

    return clauses


def _generate_turnover(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for turnover events."""
    raw = beat.event.raw
    if isinstance(raw, TurnoverEvent) and raw.is_steal:
        text_options = [
            f"stolen by {raw.stealer_name}!" if raw.stealer_name else "stolen!",
            f"{raw.stealer_name} with the steal!" if raw.stealer_name else "turnover!",
            f"picked off by {raw.stealer_name}!" if raw.stealer_name else "intercepted!",
        ]
    else:
        text_options = [
            "loses the handle! Turnover",
            "turns it over",
            "bad pass... turnover",
            "coughs it up",
        ]
    text = _pick(rng, text_options)

    return [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="turnover",
        tags={"turnover"},
    )]


def _generate_rebound(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for rebound events."""
    raw = beat.event.raw
    is_offensive = isinstance(raw, ReboundEvent) and raw.is_offensive
    name = beat.event.player_name or "the defense"

    if is_offensive:
        options = [
            f"{name} grabs the offensive board!",
            f"offensive rebound, {name}!",
            f"{name} keeps it alive!",
            f"second chance! {name} with the offensive rebound!",
        ]
    else:
        options = [
            f"{name} with the rebound",
            f"rebound, {name}",
            f"{name} grabs the board",
            f"{name} pulls it down",
        ]

    return [Clause(
        text=_pick(rng, options),
        subject=name,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="rebound",
        tags={"rebound", "offensive_rebound" if is_offensive else "defensive_rebound"},
    )]


def _generate_foul(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for foul events."""
    raw = beat.event.raw
    fouler = ""
    if isinstance(raw, FoulEvent):
        fouler = raw.fouler_name or "the defense"

    options = [
        f"foul called on {fouler}",
        f"{fouler} with the foul",
        f"whistle blows, foul on {fouler}",
        f"{fouler} reaches in... foul",
    ]

    return [Clause(
        text=_pick(rng, options),
        subject=fouler or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="foul",
        tags={"foul", "dead_ball"},
    )]


def _generate_free_throw(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for free throw events."""
    raw = beat.event.raw
    made = isinstance(raw, FreeThrowEvent) and raw.made
    name = beat.event.player_name or "the shooter"

    if made:
        options = [f"{name} hits the free throw", f"good from the line", f"{name} sinks it"]
    else:
        options = [f"{name} misses the free throw", f"no good from the line", f"{name} misses"]

    return [Clause(
        text=_pick(rng, options),
        subject=name,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="free_throw",
        tags={"free_throw"},
    )]


def _generate_probing(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Generate clauses for probing events."""
    options = get_setup_clauses("probing", band)
    text = _fill_template(_pick(rng, options), beat)

    return [Clause(
        text=text,
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type="probing",
        tags={"probing", "setup"},
    )]


def _generate_generic(
    beat: DramaticBeat, band: str, rng: SeededRNG,
) -> list[Clause]:
    """Fallback generator for unhandled event types."""
    return [Clause(
        text="the play continues",
        subject=beat.event.player_name or None,
        subject_type="handler",
        intensity=beat.intensity,
        role=beat.role,
        source_event_type=str(beat.event.raw.event_type),
        tags={"generic"},
    )]


# Dispatch table mapping event types to generators
_GENERATORS = {
    NarrationEventType.BALL_ADVANCE: _generate_ball_advance,
    NarrationEventType.DRIBBLE_MOVE: _generate_dribble_move,
    NarrationEventType.SCREEN_ACTION: _generate_screen,
    NarrationEventType.PASS_ACTION: _generate_pass,
    NarrationEventType.DRIVE: _generate_drive,
    NarrationEventType.SHOT_RESULT: _generate_shot_result,
    NarrationEventType.BLOCK: _generate_block,
    NarrationEventType.TURNOVER: _generate_turnover,
    NarrationEventType.REBOUND: _generate_rebound,
    NarrationEventType.FOUL: _generate_foul,
    NarrationEventType.FREE_THROW: _generate_free_throw,
    NarrationEventType.PROBING: _generate_probing,
}
