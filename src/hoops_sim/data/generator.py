"""Random player and team generators with archetype templates."""

from __future__ import annotations

from hoops_sim.models.attributes import (
    AthleticAttributes,
    DefensiveAttributes,
    FinishingAttributes,
    MentalAttributes,
    PlayerAttributes,
    PlaymakingAttributes,
    ReboundingAttributes,
    ShootingAttributes,
)
from hoops_sim.models.badges import BadgeTier, PlayerBadges
from hoops_sim.models.body import Handedness, HandSize, PlayerBody
from hoops_sim.models.league import CONFERENCES, League
from hoops_sim.models.player import Player, Position
from hoops_sim.models.team import Team
from hoops_sim.models.tendencies import PlayerTendencies
from hoops_sim.utils.rng import SeededRNG

# Archetype templates: baseline attributes and tendencies for player types
ARCHETYPES: dict[str, dict] = {
    "scoring_guard": {
        "positions": [Position.PG, Position.SG],
        "height_range": (73, 77),
        "weight_range": (185, 210),
        "wingspan_bonus": (0, 4),
        "primary_attrs": {"shooting": 75, "playmaking": 70, "athleticism": 72},
        "secondary_attrs": {"finishing": 68, "defense": 55, "rebounding": 40, "mental": 60},
        "tendencies": {"shot_volume": 0.75, "three_point_tendency": 0.7, "drive_tendency": 0.6},
        "common_badges": ["deadeye", "catch_and_shoot", "ankle_breaker"],
    },
    "playmaking_guard": {
        "positions": [Position.PG],
        "height_range": (72, 76),
        "weight_range": (180, 200),
        "wingspan_bonus": (0, 3),
        "primary_attrs": {"playmaking": 78, "shooting": 65, "athleticism": 70},
        "secondary_attrs": {"finishing": 65, "defense": 58, "rebounding": 38, "mental": 68},
        "tendencies": {"pass_first": 0.8, "shot_volume": 0.4, "drive_tendency": 0.5},
        "common_badges": ["dimer", "needle_threader", "floor_general", "bail_out"],
    },
    "3_and_d_wing": {
        "positions": [Position.SG, Position.SF],
        "height_range": (76, 80),
        "weight_range": (200, 225),
        "wingspan_bonus": (2, 6),
        "primary_attrs": {"shooting": 72, "defense": 74, "athleticism": 68},
        "secondary_attrs": {"finishing": 58, "playmaking": 50, "rebounding": 50, "mental": 60},
        "tendencies": {"three_point_tendency": 0.8, "shot_volume": 0.5, "closeout_aggression": 0.7},
        "common_badges": ["catch_and_shoot", "corner_specialist", "clamps", "interceptor"],
    },
    "scoring_wing": {
        "positions": [Position.SF, Position.SG],
        "height_range": (77, 81),
        "weight_range": (210, 235),
        "wingspan_bonus": (1, 5),
        "primary_attrs": {"shooting": 72, "finishing": 74, "athleticism": 73},
        "secondary_attrs": {"playmaking": 60, "defense": 58, "rebounding": 48, "mental": 58},
        "tendencies": {"shot_volume": 0.7, "drive_tendency": 0.65, "iso_tendency": 0.5},
        "common_badges": ["deadeye", "contact_finisher", "acrobat"],
    },
    "stretch_four": {
        "positions": [Position.PF],
        "height_range": (80, 83),
        "weight_range": (225, 245),
        "wingspan_bonus": (2, 5),
        "primary_attrs": {"shooting": 70, "rebounding": 65, "defense": 62},
        "secondary_attrs": {"finishing": 60, "playmaking": 45, "athleticism": 60, "mental": 55},
        "tendencies": {"three_point_tendency": 0.65, "crash_boards": 0.6, "post_up_tendency": 0.3},
        "common_badges": ["catch_and_shoot", "rebound_chaser", "box_out_beast"],
    },
    "power_forward": {
        "positions": [Position.PF],
        "height_range": (80, 84),
        "weight_range": (235, 260),
        "wingspan_bonus": (2, 6),
        "primary_attrs": {"finishing": 72, "rebounding": 72, "defense": 68},
        "secondary_attrs": {"shooting": 50, "playmaking": 45, "athleticism": 65, "mental": 55},
        "tendencies": {"post_up_tendency": 0.6, "crash_boards": 0.7, "drive_tendency": 0.4},
        "common_badges": ["contact_finisher", "rebound_chaser", "box_out_beast", "rim_protector"],
    },
    "rim_protector": {
        "positions": [Position.C],
        "height_range": (82, 87),
        "weight_range": (240, 270),
        "wingspan_bonus": (3, 8),
        "primary_attrs": {"defense": 76, "rebounding": 75, "finishing": 65},
        "secondary_attrs": {"shooting": 35, "playmaking": 38, "athleticism": 60, "mental": 55},
        "tendencies": {"crash_boards": 0.8, "contest_shots": 0.8, "help_tendency": 0.7},
        "common_badges": ["rim_protector", "intimidator", "rebound_chaser", "box_out_beast"],
    },
    "offensive_center": {
        "positions": [Position.C],
        "height_range": (82, 86),
        "weight_range": (245, 275),
        "wingspan_bonus": (2, 6),
        "primary_attrs": {"finishing": 75, "rebounding": 70, "athleticism": 62},
        "secondary_attrs": {"shooting": 45, "playmaking": 50, "defense": 60, "mental": 55},
        "tendencies": {"post_up_tendency": 0.7, "crash_boards": 0.7, "shot_volume": 0.55},
        "common_badges": ["dream_shake", "contact_finisher", "putback_boss"],
    },
    "unicorn": {
        "positions": [Position.PF, Position.C],
        "height_range": (82, 86),
        "weight_range": (225, 250),
        "wingspan_bonus": (3, 7),
        "primary_attrs": {"shooting": 72, "finishing": 70, "defense": 68},
        "secondary_attrs": {"playmaking": 55, "rebounding": 65, "athleticism": 70, "mental": 60},
        "tendencies": {"three_point_tendency": 0.5, "drive_tendency": 0.5, "crash_boards": 0.6},
        "common_badges": ["deadeye", "rim_protector", "catch_and_shoot"],
    },
    "two_way_guard": {
        "positions": [Position.PG, Position.SG],
        "height_range": (74, 78),
        "weight_range": (195, 215),
        "wingspan_bonus": (2, 5),
        "primary_attrs": {"defense": 73, "playmaking": 68, "athleticism": 72},
        "secondary_attrs": {"shooting": 62, "finishing": 62, "rebounding": 42, "mental": 62},
        "tendencies": {"gamble_for_steal": 0.5, "closeout_aggression": 0.65, "pass_first": 0.6},
        "common_badges": ["clamps", "interceptor", "dimer"],
    },
}

# Common first and last names for generation
FIRST_NAMES = [
    "James", "Michael", "Anthony", "Marcus", "Kevin", "Chris", "David",
    "Brandon", "Tyler", "Josh", "DeAndre", "Jaylen", "Darius", "Andre",
    "Malik", "Isaiah", "Tyrese", "Jalen", "Cam", "Miles", "Tre",
    "Scottie", "RJ", "Jaren", "Cade", "Evan", "Paolo", "Victor",
    "Zion", "Ja", "Luka", "Trae", "Shai", "Devin", "Donovan",
]

LAST_NAMES = [
    "Johnson", "Williams", "Brown", "Davis", "Smith", "Jones", "Jackson",
    "Thomas", "Harris", "Robinson", "Thompson", "Walker", "Green", "White",
    "Mitchell", "Young", "King", "Wright", "Carter", "Turner", "Hill",
    "Murray", "Edwards", "Barnes", "Bridges", "Holiday", "Gordon", "Porter",
    "Brooks", "Coleman", "Washington", "Reed", "Graham", "Henderson", "Price",
]


def generate_player(
    rng: SeededRNG,
    archetype: str | None = None,
    age: int | None = None,
    overall_target: int | None = None,
) -> Player:
    """Generate a random player from an archetype template.

    Args:
        rng: Seeded RNG for deterministic generation.
        archetype: Archetype key (random if None).
        age: Player age (random 19-35 if None).
        overall_target: Target overall rating to scale to (None = use archetype base).

    Returns:
        A fully configured Player.
    """
    if archetype is None:
        archetype = rng.choice(list(ARCHETYPES.keys()))

    template = ARCHETYPES[archetype]

    # Identity
    first_name = rng.choice(FIRST_NAMES)
    last_name = rng.choice(LAST_NAMES)
    player_age = age if age is not None else rng.randint(19, 35)
    position = rng.choice(template["positions"])
    secondary = None
    if len(template["positions"]) > 1:
        others = [p for p in template["positions"] if p != position]
        if others:
            secondary = rng.choice(others)

    # Body
    h_lo, h_hi = template["height_range"]
    height = rng.randint(h_lo, h_hi)
    w_lo, w_hi = template["weight_range"]
    weight = rng.randint(w_lo, w_hi)
    ws_lo, ws_hi = template["wingspan_bonus"]
    wingspan = height + rng.randint(ws_lo, ws_hi)
    standing_reach = int(height * 1.33 + rng.randint(-2, 2))
    handedness = Handedness.LEFT if rng.random() < 0.12 else Handedness.RIGHT
    hand_sizes = [HandSize.SMALL, HandSize.AVERAGE, HandSize.LARGE, HandSize.EXTRA_LARGE]
    hand_size = rng.choices(hand_sizes, weights=[10, 50, 30, 10], k=1)[0]

    body = PlayerBody(
        height_inches=height,
        weight_lbs=weight,
        wingspan_inches=wingspan,
        standing_reach_inches=standing_reach,
        body_fat_pct=round(rng.uniform(5.0, 12.0), 1),
        hand_size=hand_size,
        handedness=handedness,
        shoe_size=round(rng.uniform(12.0, 18.0), 1),
    )

    # Attributes with variance
    def _gen_attr(base: int) -> int:
        scale = 1.0
        if overall_target is not None:
            scale = overall_target / 65.0  # 65 is roughly the average base
        val = int(base * scale + rng.gauss(0, 6))
        # Age curve: prime is 26-30, decline after 32
        if player_age < 22:
            val = int(val * 0.88)
        elif player_age < 25:
            val = int(val * 0.95)
        elif player_age > 33:
            val = int(val * 0.90)
        elif player_age > 30:
            val = int(val * 0.95)
        return max(25, min(99, val))

    primary = template["primary_attrs"]
    secondary_a = template["secondary_attrs"]

    def _base(category: str) -> int:
        return primary.get(category, secondary_a.get(category, 50))

    attrs = PlayerAttributes(
        shooting=ShootingAttributes(
            close_shot=_gen_attr(_base("shooting") - 3),
            mid_range=_gen_attr(_base("shooting")),
            three_point=_gen_attr(_base("shooting") + 2),
            free_throw=_gen_attr(_base("shooting") + 5),
            shot_iq=_gen_attr(_base("mental")),
            shot_consistency=_gen_attr(_base("shooting") - 2),
            shot_speed=_gen_attr(_base("shooting") - 5),
        ),
        finishing=FinishingAttributes(
            layup=_gen_attr(_base("finishing") + 5),
            standing_dunk=_gen_attr(_base("finishing") - 5),
            driving_dunk=_gen_attr(_base("finishing")),
            draw_foul=_gen_attr(_base("finishing") - 3),
            acrobatic_finish=_gen_attr(_base("finishing") - 2),
            post_hook=_gen_attr(_base("finishing") - 8),
            post_fadeaway=_gen_attr(_base("finishing") - 8),
            post_moves=_gen_attr(_base("finishing") - 10),
        ),
        playmaking=PlaymakingAttributes(
            ball_handle=_gen_attr(_base("playmaking")),
            pass_accuracy=_gen_attr(_base("playmaking") + 2),
            pass_vision=_gen_attr(_base("playmaking") - 2),
            pass_iq=_gen_attr(_base("playmaking")),
            speed_with_ball=_gen_attr(_base("playmaking") - 3),
            hands=_gen_attr(_base("playmaking") - 5),
        ),
        defense=DefensiveAttributes(
            interior_defense=_gen_attr(_base("defense") - 3),
            perimeter_defense=_gen_attr(_base("defense")),
            lateral_quickness=_gen_attr(_base("defense") + 2),
            steal=_gen_attr(_base("defense") - 5),
            block=_gen_attr(_base("defense") - 8),
            defensive_iq=_gen_attr(_base("defense") + 3),
            defensive_consistency=_gen_attr(_base("defense")),
            pick_dodger=_gen_attr(_base("defense") - 2),
            help_defense_iq=_gen_attr(_base("defense")),
            on_ball_defense=_gen_attr(_base("defense") + 2),
        ),
        rebounding=ReboundingAttributes(
            offensive_rebound=_gen_attr(_base("rebounding") - 5),
            defensive_rebound=_gen_attr(_base("rebounding") + 5),
            box_out=_gen_attr(_base("rebounding")),
        ),
        athleticism=AthleticAttributes(
            speed=_gen_attr(_base("athleticism") + 3),
            acceleration=_gen_attr(_base("athleticism") + 2),
            vertical_leap=_gen_attr(_base("athleticism")),
            strength=_gen_attr(50 + weight // 8),
            stamina=_gen_attr(_base("athleticism") - 2),
            hustle=_gen_attr(_base("mental")),
            durability=_gen_attr(65),
        ),
        mental=MentalAttributes(
            basketball_iq=_gen_attr(_base("mental") + 3),
            clutch=_gen_attr(_base("mental") - 5),
            composure=_gen_attr(_base("mental")),
            work_ethic=_gen_attr(_base("mental")),
            coachability=_gen_attr(_base("mental") + 2),
            leadership=_gen_attr(_base("mental") - 5 + min(15, player_age - 20)),
            mentorship=_gen_attr(max(30, _base("mental") - 15 + player_age - 25)),
            motor=_gen_attr(_base("mental")),
        ),
    )

    # Tendencies from template
    t_template = template.get("tendencies", {})
    tendencies = PlayerTendencies(**{
        k: max(0.0, min(1.0, v + rng.gauss(0, 0.1)))
        for k, v in t_template.items()
    })

    # Badges from template
    badges = PlayerBadges()
    for badge_key in template.get("common_badges", []):
        # Higher overall players get higher tier badges
        base_ovr = attrs.overall()
        if base_ovr >= 85:
            tier = BadgeTier.HALL_OF_FAME if rng.random() < 0.3 else BadgeTier.GOLD
        elif base_ovr >= 75:
            tier = BadgeTier.GOLD if rng.random() < 0.3 else BadgeTier.SILVER
        elif base_ovr >= 65:
            tier = BadgeTier.SILVER if rng.random() < 0.3 else BadgeTier.BRONZE
        else:
            tier = BadgeTier.BRONZE
        badges.add_badge(badge_key, tier)

    return Player(
        id=rng.randint(1, 999999),
        first_name=first_name,
        last_name=last_name,
        age=player_age,
        position=position,
        secondary_position=secondary,
        jersey_number=rng.randint(0, 99),
        years_pro=max(0, player_age - 19 - rng.randint(0, 3)),
        body=body,
        attributes=attrs,
        tendencies=tendencies,
        badges=badges,
    )


def generate_roster(rng: SeededRNG, size: int = 15) -> list[Player]:
    """Generate a full roster with balanced positions.

    Args:
        rng: Seeded RNG.
        size: Number of players (default 15).

    Returns:
        List of generated Players.
    """
    # Ensure position balance: 2 PG, 2 SG, 2 SF, 2 PF, 2 C + 5 flex
    position_archetypes = [
        "playmaking_guard", "scoring_guard",  # PG/SG
        "scoring_guard", "3_and_d_wing",  # SG/SF
        "scoring_wing", "3_and_d_wing",  # SF
        "stretch_four", "power_forward",  # PF
        "rim_protector", "offensive_center",  # C
    ]

    flex_archetypes = list(ARCHETYPES.keys())
    players = []

    for i in range(size):
        if i < len(position_archetypes):
            archetype = position_archetypes[i]
        else:
            archetype = rng.choice(flex_archetypes)

        # Starters are better (higher overall target)
        if i < 5:
            overall_target = rng.randint(72, 85)
        elif i < 10:
            overall_target = rng.randint(62, 75)
        else:
            overall_target = rng.randint(55, 68)

        player = generate_player(rng, archetype=archetype, overall_target=overall_target)
        players.append(player)

    return players


# Team name data for league generation
TEAM_DATA = [
    ("New York", "Knicks", "NYK", "East", "Atlantic"),
    ("Boston", "Celtics", "BOS", "East", "Atlantic"),
    ("Philadelphia", "76ers", "PHI", "East", "Atlantic"),
    ("Toronto", "Raptors", "TOR", "East", "Atlantic"),
    ("Brooklyn", "Nets", "BKN", "East", "Atlantic"),
    ("Milwaukee", "Bucks", "MIL", "East", "Central"),
    ("Cleveland", "Cavaliers", "CLE", "East", "Central"),
    ("Chicago", "Bulls", "CHI", "East", "Central"),
    ("Indiana", "Pacers", "IND", "East", "Central"),
    ("Detroit", "Pistons", "DET", "East", "Central"),
    ("Miami", "Heat", "MIA", "East", "Southeast"),
    ("Atlanta", "Hawks", "ATL", "East", "Southeast"),
    ("Orlando", "Magic", "ORL", "East", "Southeast"),
    ("Charlotte", "Hornets", "CHA", "East", "Southeast"),
    ("Washington", "Wizards", "WAS", "East", "Southeast"),
    ("Denver", "Nuggets", "DEN", "West", "Northwest"),
    ("Minnesota", "Timberwolves", "MIN", "West", "Northwest"),
    ("Oklahoma City", "Thunder", "OKC", "West", "Northwest"),
    ("Utah", "Jazz", "UTA", "West", "Northwest"),
    ("Portland", "Trail Blazers", "POR", "West", "Northwest"),
    ("Golden State", "Warriors", "GSW", "West", "Pacific"),
    ("LA", "Lakers", "LAL", "West", "Pacific"),
    ("LA", "Clippers", "LAC", "West", "Pacific"),
    ("Phoenix", "Suns", "PHX", "West", "Pacific"),
    ("Sacramento", "Kings", "SAC", "West", "Pacific"),
    ("Dallas", "Mavericks", "DAL", "West", "Southwest"),
    ("Houston", "Rockets", "HOU", "West", "Southwest"),
    ("Memphis", "Grizzlies", "MEM", "West", "Southwest"),
    ("New Orleans", "Pelicans", "NOP", "West", "Southwest"),
    ("San Antonio", "Spurs", "SAS", "West", "Southwest"),
]


def generate_league(num_teams: int = 30, rng: Optional[SeededRNG] = None) -> League:
    """Generate a full league with teams and rosters.

    Args:
        num_teams: Number of teams to generate (max 30).
        rng: Seeded RNG for deterministic generation.

    Returns:
        A fully populated League.
    """
    if rng is None:
        rng = SeededRNG(seed=42)

    num_teams = min(num_teams, len(TEAM_DATA))
    league = League(season_year=2025)
    teams: List[Team] = []

    for i in range(num_teams):
        city, name, abbr, conf, div = TEAM_DATA[i]
        roster = generate_roster(rng, size=15)
        team = Team(
            id=i + 1,
            city=city,
            name=name,
            abbreviation=abbr,
            conference=conf,
            division=div,
            roster=roster,
        )
        teams.append(team)

    league.teams = teams
    return league
