"""Offensive play definitions and playbook system.

Each play defines a structured sequence of actions: screens, cuts, passes,
and shot options. The coach AI selects plays based on game situation,
personnel, and matchups. Players execute their assigned roles each possession.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field


class PlayType(enum.Enum):
    """Categories of offensive plays."""

    PICK_AND_ROLL = "pick_and_roll"
    ISOLATION = "isolation"
    MOTION = "motion"
    POST_UP = "post_up"
    FAST_BREAK = "fast_break"
    OFF_SCREEN = "off_screen"
    HANDOFF = "handoff"
    CUT = "cut"
    # New play types from the micro-action overhaul
    HORNS = "horns"
    FLOPPY = "floppy"
    SPAIN_PNR = "spain_pnr"
    DHO = "dho"
    UCLA_CUT = "ucla_cut"
    DELAY = "delay"
    ATO = "ato"


class PlayerRole(enum.Enum):
    """Role a player fills in a play."""

    BALL_HANDLER = "ball_handler"
    SCREENER = "screener"
    SHOOTER = "shooter"  # Spot-up / relocate
    CUTTER = "cutter"
    POST_PLAYER = "post_player"
    SPACER = "spacer"  # Stand in a spot and stretch the defense


@dataclass
class PlayAction:
    """A single step in a play sequence."""

    action: str  # "screen", "cut", "pass", "dribble", "shoot", "relocate"
    role: PlayerRole  # Which role performs this action
    target_role: PlayerRole | None = None  # For passes/screens: who's the target
    description: str = ""


@dataclass
class PlayDefinition:
    """A complete offensive play definition."""

    name: str
    play_type: PlayType
    description: str = ""

    # Roles needed (maps position index 0-4 to roles)
    roles: list[PlayerRole] = field(default_factory=list)

    # Sequence of actions that make up the play
    actions: list[PlayAction] = field(default_factory=list)

    # Shot quality modifiers when the play is executed well
    shot_quality_bonus: float = 0.0  # 0-0.15 bonus to shot quality
    drive_quality_bonus: float = 0.0
    pass_quality_bonus: float = 0.0

    # Situational fit scores (0-1, higher = better fit)
    transition_fit: float = 0.0  # How good in transition
    halfcourt_fit: float = 1.0  # How good in half-court
    clutch_fit: float = 0.5  # How good in clutch
    comeback_fit: float = 0.5  # How good when trailing


# -- Built-in play definitions ------------------------------------------------

PICK_AND_ROLL = PlayDefinition(
    name="Pick and Roll",
    play_type=PlayType.PICK_AND_ROLL,
    description="Ball handler uses a screen from the big, reads the defense for a pull-up, "
    "drive, or pass to the rolling screener.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SCREENER,
        PlayerRole.SHOOTER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.BALL_HANDLER,
                   "Big sets screen for ball handler"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Ball handler uses screen, reads defense"),
        PlayAction("cut", PlayerRole.SCREENER, None,
                   "Screener rolls to the basket"),
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.SCREENER,
                   "Hit the roller if open"),
        PlayAction("shoot", PlayerRole.BALL_HANDLER, None,
                   "Pull-up jumper if defense goes under"),
    ],
    shot_quality_bonus=0.08,
    drive_quality_bonus=0.10,
    pass_quality_bonus=0.05,
    halfcourt_fit=0.9,
    clutch_fit=0.7,
)

ISOLATION = PlayDefinition(
    name="Isolation",
    play_type=PlayType.ISOLATION,
    description="Clear out one side for the best scorer to go one-on-one.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Ball handler sizes up defender"),
        PlayAction("shoot", PlayerRole.BALL_HANDLER, None,
                   "Pull-up or drive to score"),
    ],
    shot_quality_bonus=0.03,
    drive_quality_bonus=0.12,
    halfcourt_fit=0.6,
    clutch_fit=0.9,
    comeback_fit=0.4,
)

MOTION_OFFENSE = PlayDefinition(
    name="Motion Offense",
    play_type=PlayType.MOTION,
    description="Read-and-react offense with constant cutting, screening, and ball movement.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.CUTTER,
        PlayerRole.SHOOTER,
        PlayerRole.CUTTER,
        PlayerRole.SCREENER,
    ],
    actions=[
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.SHOOTER,
                   "Swing the ball"),
        PlayAction("cut", PlayerRole.CUTTER, None,
                   "Back-door cut to the basket"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.SHOOTER,
                   "Off-ball screen for the shooter"),
        PlayAction("relocate", PlayerRole.SHOOTER, None,
                   "Shooter relocates off screen"),
        PlayAction("shoot", PlayerRole.SHOOTER, None,
                   "Catch and shoot"),
    ],
    shot_quality_bonus=0.10,
    pass_quality_bonus=0.12,
    halfcourt_fit=1.0,
    clutch_fit=0.5,
)

POST_UP = PlayDefinition(
    name="Post Up",
    play_type=PlayType.POST_UP,
    description="Feed the post player and let them work in the low block.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.POST_PLAYER,
        PlayerRole.SHOOTER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.POST_PLAYER,
                   "Entry pass to the post"),
        PlayAction("dribble", PlayerRole.POST_PLAYER, None,
                   "Post player backs down defender"),
        PlayAction("shoot", PlayerRole.POST_PLAYER, None,
                   "Hook shot, fadeaway, or drop step"),
    ],
    shot_quality_bonus=0.06,
    halfcourt_fit=0.7,
    clutch_fit=0.6,
)

FAST_BREAK = PlayDefinition(
    name="Fast Break",
    play_type=PlayType.FAST_BREAK,
    description="Push the ball in transition for an easy bucket before the defense sets.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.CUTTER,
        PlayerRole.CUTTER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Push the ball up court"),
        PlayAction("cut", PlayerRole.CUTTER, None,
                   "Fill the lane"),
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.CUTTER,
                   "Hit the cutter for the layup"),
    ],
    shot_quality_bonus=0.12,
    drive_quality_bonus=0.15,
    transition_fit=1.0,
    halfcourt_fit=0.0,
    clutch_fit=0.3,
)

OFF_SCREEN_ACTION = PlayDefinition(
    name="Off-Screen Action",
    play_type=PlayType.OFF_SCREEN,
    description="Run a shooter off multiple screens for a catch-and-shoot three.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SCREENER,
        PlayerRole.SCREENER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.SHOOTER,
                   "First screen for the shooter"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.SHOOTER,
                   "Second screen (stagger)"),
        PlayAction("relocate", PlayerRole.SHOOTER, None,
                   "Shooter curls off screens"),
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.SHOOTER,
                   "Hit the shooter coming off"),
        PlayAction("shoot", PlayerRole.SHOOTER, None,
                   "Catch and shoot three"),
    ],
    shot_quality_bonus=0.12,
    pass_quality_bonus=0.08,
    halfcourt_fit=0.8,
    clutch_fit=0.6,
)

HANDOFF = PlayDefinition(
    name="Dribble Handoff",
    play_type=PlayType.HANDOFF,
    description="Big brings the ball up and hands off to a guard for a drive or pull-up.",
    roles=[
        PlayerRole.SCREENER,
        PlayerRole.BALL_HANDLER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("dribble", PlayerRole.SCREENER, None,
                   "Big dribbles toward the wing"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.BALL_HANDLER,
                   "Handoff with screening action"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Guard comes off the handoff"),
        PlayAction("shoot", PlayerRole.BALL_HANDLER, None,
                   "Pull-up or drive"),
    ],
    shot_quality_bonus=0.07,
    drive_quality_bonus=0.08,
    halfcourt_fit=0.8,
    clutch_fit=0.5,
)

# -- New plays from the micro-action overhaul ---------------------------------

HORNS = PlayDefinition(
    name="Horns",
    play_type=PlayType.HORNS,
    description="Two bigs at the elbows. PG picks a side for PnR with either big, "
    "while the other pops or dives. Creates multiple options off one formation.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SCREENER,
        PlayerRole.SCREENER,
        PlayerRole.SHOOTER,
        PlayerRole.SHOOTER,
    ],
    actions=[
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "PG surveys at top of key"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.BALL_HANDLER,
                   "Elbow big sets ball screen"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "PG uses screen, reads defense"),
        PlayAction("cut", PlayerRole.SCREENER, None,
                   "Screening big rolls to basket"),
        PlayAction("relocate", PlayerRole.SCREENER, None,
                   "Opposite big pops to three-point line"),
    ],
    shot_quality_bonus=0.09,
    drive_quality_bonus=0.10,
    pass_quality_bonus=0.08,
    halfcourt_fit=0.9,
    clutch_fit=0.7,
    comeback_fit=0.6,
)

FLOPPY = PlayDefinition(
    name="Floppy",
    play_type=PlayType.FLOPPY,
    description="Shooter starts at the free-throw line and chooses to come off "
    "stagger screens on either side. Creates a catch-and-shoot opportunity.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SHOOTER,
        PlayerRole.SCREENER,
        PlayerRole.SCREENER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.SHOOTER,
                   "First down screen for the shooter"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.SHOOTER,
                   "Second screen in stagger"),
        PlayAction("relocate", PlayerRole.SHOOTER, None,
                   "Shooter curls off screens to the wing"),
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.SHOOTER,
                   "Hit the shooter coming off the stagger"),
        PlayAction("shoot", PlayerRole.SHOOTER, None,
                   "Catch and shoot three"),
    ],
    shot_quality_bonus=0.12,
    pass_quality_bonus=0.10,
    halfcourt_fit=0.85,
    clutch_fit=0.65,
)

SPAIN_PNR = PlayDefinition(
    name="Spain Pick and Roll",
    play_type=PlayType.SPAIN_PNR,
    description="Standard PnR with a wrinkle: a third player sets a back screen "
    "on the screener's defender, freeing the roller. Devastating when executed well.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SCREENER,
        PlayerRole.CUTTER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.BALL_HANDLER,
                   "Big sets ball screen"),
        PlayAction("screen", PlayerRole.CUTTER, PlayerRole.SCREENER,
                   "Third player back-screens the big's defender"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Handler uses the screen, reads the defense"),
        PlayAction("cut", PlayerRole.SCREENER, None,
                   "Big rolls free after the back screen"),
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.SCREENER,
                   "Lob or bounce to the wide-open roller"),
    ],
    shot_quality_bonus=0.10,
    drive_quality_bonus=0.12,
    pass_quality_bonus=0.10,
    halfcourt_fit=0.85,
    clutch_fit=0.6,
)

DHO = PlayDefinition(
    name="Dribble Handoff",
    play_type=PlayType.DHO,
    description="Big receives the ball at the elbow and hands off to a guard "
    "curling around. The handoff acts as a screen, creating a pull-up or drive.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.POST_PLAYER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("pass", PlayerRole.BALL_HANDLER, PlayerRole.POST_PLAYER,
                   "Entry pass to the big at the elbow"),
        PlayAction("screen", PlayerRole.POST_PLAYER, PlayerRole.BALL_HANDLER,
                   "Big hands off with a screening action"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Guard comes off the handoff"),
        PlayAction("shoot", PlayerRole.BALL_HANDLER, None,
                   "Pull-up jumper or drive to the rim"),
    ],
    shot_quality_bonus=0.08,
    drive_quality_bonus=0.09,
    halfcourt_fit=0.8,
    clutch_fit=0.55,
)

UCLA_CUT = PlayDefinition(
    name="UCLA Cut",
    play_type=PlayType.UCLA_CUT,
    description="Guard passes to the wing and cuts off a screen to the basket. "
    "Creates a layup opportunity or opens up the wing for a three.",
    roles=[
        PlayerRole.CUTTER,
        PlayerRole.SCREENER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("pass", PlayerRole.CUTTER, PlayerRole.SHOOTER,
                   "Guard passes to the wing"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.CUTTER,
                   "High post big sets screen for cutter"),
        PlayAction("cut", PlayerRole.CUTTER, None,
                   "Guard cuts off the screen to the basket"),
        PlayAction("pass", PlayerRole.SHOOTER, PlayerRole.CUTTER,
                   "Hit the cutter for the layup"),
    ],
    shot_quality_bonus=0.10,
    drive_quality_bonus=0.08,
    pass_quality_bonus=0.06,
    halfcourt_fit=0.85,
    clutch_fit=0.5,
)

DELAY = PlayDefinition(
    name="Delay",
    play_type=PlayType.DELAY,
    description="Hold the ball and let the shot clock wind down, then attack "
    "with a designed action. Used when protecting a lead late in games.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Ball handler dribbles at top of key, killing clock"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Continue probing, looking for an opening"),
        PlayAction("shoot", PlayerRole.BALL_HANDLER, None,
                   "Attack with under 7 seconds on the shot clock"),
    ],
    shot_quality_bonus=0.03,
    drive_quality_bonus=0.05,
    halfcourt_fit=0.5,
    clutch_fit=0.8,
    comeback_fit=0.1,
)

ATO = PlayDefinition(
    name="After Timeout",
    play_type=PlayType.ATO,
    description="Designed play drawn up during a timeout. Typically features "
    "misdirection and a specific scoring action for the best player.",
    roles=[
        PlayerRole.BALL_HANDLER,
        PlayerRole.SCREENER,
        PlayerRole.CUTTER,
        PlayerRole.SHOOTER,
        PlayerRole.SPACER,
    ],
    actions=[
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.SHOOTER,
                   "Off-ball screen to create misdirection"),
        PlayAction("cut", PlayerRole.CUTTER, None,
                   "Cutter goes backdoor as a decoy"),
        PlayAction("screen", PlayerRole.SCREENER, PlayerRole.BALL_HANDLER,
                   "Second screen for the primary option"),
        PlayAction("dribble", PlayerRole.BALL_HANDLER, None,
                   "Ball handler uses screen for the designed shot"),
        PlayAction("shoot", PlayerRole.BALL_HANDLER, None,
                   "Take the designed shot"),
    ],
    shot_quality_bonus=0.12,
    drive_quality_bonus=0.08,
    pass_quality_bonus=0.06,
    halfcourt_fit=0.9,
    clutch_fit=0.95,
    comeback_fit=0.7,
)


# All plays available in the default playbook
DEFAULT_PLAYBOOK: list[PlayDefinition] = [
    PICK_AND_ROLL,
    ISOLATION,
    MOTION_OFFENSE,
    POST_UP,
    FAST_BREAK,
    OFF_SCREEN_ACTION,
    HANDOFF,
    HORNS,
    FLOPPY,
    SPAIN_PNR,
    DHO,
    UCLA_CUT,
    DELAY,
    ATO,
]


def select_play(
    playbook: list[PlayDefinition],
    is_transition: bool = False,
    is_clutch: bool = False,
    is_trailing: bool = False,
    has_post_player: bool = True,
    rng_value: float = 0.5,
) -> PlayDefinition:
    """Select a play from the playbook based on game situation.

    Args:
        playbook: Available plays.
        is_transition: Whether this is a transition opportunity.
        is_clutch: Whether it's clutch time.
        is_trailing: Whether the team is trailing.
        has_post_player: Whether there's a capable post player on court.
        rng_value: Random value [0,1) for weighted selection.

    Returns:
        The selected PlayDefinition.
    """
    if not playbook:
        return PICK_AND_ROLL

    weights: list[float] = []
    for play in playbook:
        w = 1.0
        if is_transition:
            w *= (play.transition_fit + 0.1)
        else:
            w *= (play.halfcourt_fit + 0.1)
        if is_clutch:
            w *= (play.clutch_fit + 0.1)
        if is_trailing:
            w *= (play.comeback_fit + 0.1)
        if play.play_type == PlayType.POST_UP and not has_post_player:
            w *= 0.1
        weights.append(max(w, 0.01))

    total = sum(weights)
    threshold = rng_value * total
    cumulative = 0.0
    for i, w in enumerate(weights):
        cumulative += w
        if threshold <= cumulative:
            return playbook[i]
    return playbook[-1]
