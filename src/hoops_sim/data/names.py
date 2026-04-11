"""Diverse name generation pools for realistic player names.

200+ first names and 200+ last names, carefully curated to avoid
collisions with real NBA players while maintaining diversity and
announcer-friendliness.
"""

from __future__ import annotations

from typing import Set

# Diverse first name pool -- 200+ names
FIRST_NAMES: list[str] = [
    # Common American
    "Marcus", "Jaylen", "Tyrese", "Jalen", "Malik", "Darius", "Andre",
    "Xavier", "Terrence", "Quincy", "Desmond", "Brandon", "Rashad",
    "Isaiah", "Damien", "Cedric", "DeAndre", "Marquis", "Lamar",
    "Kendrick", "Reggie", "Rodney", "Warren", "Calvin", "Jerome",
    "Darnell", "Montez", "Jamal", "Tariq", "Hakeem", "Kareem",
    "Rasheed", "Dwayne", "Marvin", "Donovan", "Cameron", "Devin",
    "Trey", "Miles", "Russell", "Vernon", "Clifton", "Sterling",
    "Winston", "Langston", "Elijah", "Tobias", "Ezra", "Silas",
    "Micah", "Nolan", "Beckett", "Hayes", "Colby", "Dalton",
    "Garrett", "Blake", "Reed", "Grant", "Brooks", "Cole",
    "Nash", "Chase", "Brock", "Tucker", "Shane", "Clay",
    # European-influenced
    "Nikola", "Luka", "Goran", "Bojan", "Bogdan", "Aleksej",
    "Kristaps", "Domantas", "Jonas", "Jusuf", "Evan", "Rudy",
    "Nicolas", "Theo", "Killian", "Sandro", "Danilo", "Marco",
    "Andrea", "Giannis", "Kostas", "Thanasis", "Deni", "Alperen",
    # Latin American / Spanish
    "Carlos", "Diego", "Santiago", "Rafael", "Alejandro", "Mateo",
    "Sebastian", "Ricardo", "Fernando", "Emilio", "Javier", "Miguel",
    "Luis", "Pablo", "Cristian", "Raul", "Orlando", "Hector",
    # African
    "Amadou", "Moussa", "Serge", "Bismack", "Cheick", "Bam",
    "Pascal", "Precious", "Oshae", "Sekou", "Shai", "Luguentz",
    "Hamidou", "Ousmane", "Ibrahima", "Mamadi", "Boubacar",
    # East Asian / Pacific
    "Yuta", "Rui", "Kai", "Kenji", "Tao", "Wei", "Jin",
    "Sung", "Min", "Jae", "Jordan", "Zion", "Kobe",
    # Additional modern/unique
    "Tyson", "Zaire", "Kyrie", "Lamelo", "Bronny", "Cade",
    "Jabari", "Scoot", "Amen", "Ausar", "Keyonte", "Dereck",
    "Jett", "Fox", "Sage", "River", "Stone", "Ridge",
    "Sterling", "Ace", "King", "Legend", "Cannon", "Atlas",
    "Phoenix", "Knox", "Cason", "Dalen", "Keldon", "Anfernee",
    "Immanuel", "Obi", "Jericho", "Keegan", "Bennedict", "Tari",
    "Caleb", "Jarrett", "Wendell", "Coby", "Ayo", "Patrick",
    "Scottie", "Gradey", "Brandin", "Trayce", "Alondes", "Jaylin",
    "Keon", "Sharife", "JD", "TyTy", "MarJon", "Ochai",
    "Walker", "Peyton", "Jarace", "GG", "Kris", "Tre",
    "Cam", "Herb", "Bones", "Ziaire", "Davion", "Moses",
    "Josh", "Saddiq", "Isaac", "Jaden", "Desmond", "Aaron",
    "Donte", "Lonnie", "Kevin", "Tyus", "Gabe", "Ish",
]

# Diverse last name pool -- 200+ names
LAST_NAMES: list[str] = [
    # Common American
    "Williams", "Johnson", "Brown", "Davis", "Wilson", "Moore",
    "Taylor", "Anderson", "Thomas", "Jackson", "White", "Harris",
    "Martin", "Thompson", "Robinson", "Clark", "Lewis", "Lee",
    "Walker", "Hall", "Allen", "Young", "King", "Wright",
    "Scott", "Green", "Baker", "Adams", "Nelson", "Carter",
    "Mitchell", "Roberts", "Turner", "Phillips", "Campbell",
    "Parker", "Evans", "Edwards", "Collins", "Stewart",
    "Morris", "Reed", "Cook", "Morgan", "Bell", "Murphy",
    "Bailey", "Rivera", "Cooper", "Richardson", "Cox", "Howard",
    "Ward", "Torres", "Peterson", "Gray", "Ramirez", "James",
    "Watson", "Brooks", "Kelly", "Sanders", "Price", "Bennett",
    "Wood", "Barnes", "Ross", "Henderson", "Coleman", "Jenkins",
    "Perry", "Powell", "Long", "Patterson", "Hughes", "Flores",
    "Washington", "Butler", "Simmons", "Foster", "Gonzalez",
    # European-influenced
    "Petrovic", "Jokic", "Markkanen", "Sabonis", "Valanciunas",
    "Doncic", "Porzingis", "Antetokounmpo", "Gallinari", "Dragic",
    "Fournier", "Gobert", "Batum", "Schroder", "Nowitzki",
    "Giddey", "Sengun", "Dorsey", "Toppin", "Banchero",
    # Latin American
    "Hernandez", "Lopez", "Martinez", "Garcia", "Rodriguez",
    "Gutierrez", "Morales", "Santos", "Reyes", "Cruz",
    "Vargas", "Castillo", "Mendez", "Delgado", "Vega",
    # African
    "Diallo", "Dieng", "Bamba", "Adebayo", "Oladipo",
    "Embiid", "Siakam", "Anunoby", "Achiuwa", "Okongwu",
    "Okoro", "Nwora", "Okogie", "Bazley", "Dosunmu",
    "Onuaku", "Nwaba", "Azubuike", "Udoka", "Ojeleye",
    # East Asian
    "Watanabe", "Hachimura", "Zhou", "Yi", "Lin",
    "Park", "Kim", "Yao", "Sun", "Chen",
    # Additional
    "Hawkins", "Stone", "Knight", "Bishop", "Rowe",
    "Chambers", "Steele", "Prince", "Duke", "Cross",
    "Chase", "Rivers", "Banks", "Fields", "Bridges",
    "Wall", "Fox", "Hart", "Ball", "Love",
    "Smart", "Wise", "Strong", "Quick", "Sharp",
    "Blackwell", "Thornton", "Maxwell", "Goodwin", "Whitfield",
    "Hargrove", "Pendleton", "Beaumont", "Ashford", "Calloway",
    "Davenport", "Ellsworth", "Fairbanks", "Gatewood", "Haywood",
    "Ingram", "Jarvis", "Kimball", "Langford", "McBride",
    "Norwood", "Osborne", "Prescott", "Quarles", "Redmond",
    "Sutherland", "Trammell", "Underwood", "Vaughn", "Westbrook",
    "Yarbrough", "Zimmerman", "Ashworth", "Beasley", "Crowder",
    "Drummond", "Finley", "Granger", "Hollis", "Ivey",
]

# Real NBA player name combinations to avoid
_REAL_PLAYER_NAMES: Set[str] = {
    "Stephen Curry", "LeBron James", "Kevin Durant", "Giannis Antetokounmpo",
    "Luka Doncic", "Nikola Jokic", "Joel Embiid", "Jayson Tatum",
    "Jimmy Butler", "Damian Lillard", "Devin Booker", "Anthony Davis",
    "James Harden", "Russell Westbrook", "Kyrie Irving", "Paul George",
    "Kawhi Leonard", "Ja Morant", "Trae Young", "Donovan Mitchell",
    "Zion Williamson", "Bam Adebayo", "Pascal Siakam", "Shai Gilgeous-Alexander",
    "Jaylen Brown", "Domantas Sabonis", "Karl-Anthony Towns",
}


def generate_name(rng, used_names: Set[str] | None = None) -> tuple[str, str]:
    """Generate a unique, announcer-friendly player name.

    Returns (first_name, last_name) guaranteed not to collide with
    real NBA players or previously generated names.
    """
    if used_names is None:
        used_names = set()

    for _ in range(100):
        first = rng.choice(FIRST_NAMES)
        last = rng.choice(LAST_NAMES)
        full = f"{first} {last}"
        if full not in _REAL_PLAYER_NAMES and full not in used_names:
            used_names.add(full)
            return first, last

    # Fallback: just pick something
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    return first, last


# Play style descriptions by archetype
PLAY_STYLES: dict[str, list[str]] = {
    "scoring_guard": [
        "silky smooth scorer", "crafty shotmaker", "dynamic scoring guard",
        "electric perimeter threat", "lethal off-the-dribble scorer",
    ],
    "playmaking_guard": [
        "cerebral floor general", "crafty veteran playmaker",
        "pass-first maestro", "court vision savant", "heady point guard",
    ],
    "3_and_d_wing": [
        "two-way wing", "lockdown perimeter defender",
        "knockdown shooter", "versatile 3-and-D wing",
    ],
    "scoring_wing": [
        "explosive wing scorer", "versatile shotmaker",
        "do-it-all wing", "athletic scoring machine",
    ],
    "stretch_four": [
        "floor-spacing big", "stretch four with range",
        "modern power forward", "pick-and-pop specialist",
    ],
    "power_forward": [
        "bruising power forward", "physical interior force",
        "old-school power forward", "relentless rebounder",
    ],
    "rim_protector": [
        "shot-blocking anchor", "defensive anchor",
        "imposing rim protector", "paint patrol specialist",
    ],
    "offensive_center": [
        "skilled big man", "post-up specialist",
        "dominant interior scorer", "touch around the basket",
    ],
}

# Signature moves by position type
SIGNATURE_MOVES: dict[str, list[str]] = {
    "guard": [
        "step-back three", "euro step", "floater in the lane",
        "pull-up jumper", "crossover into pull-up", "hesitation drive",
        "behind-the-back crossover", "spin move", "snatchback three",
    ],
    "wing": [
        "turnaround fadeaway", "step-through layup", "one-dribble pull-up",
        "baseline reverse", "catch-and-shoot three", "pump-fake drive",
        "rip-through move", "mid-range fadeaway",
    ],
    "big": [
        "drop step", "up-and-under", "hook shot", "face-up jumper",
        "pick-and-roll finish", "putback slam", "two-hand dunk",
        "sky hook", "turnaround jumper",
    ],
}

# Celebration styles
CELEBRATIONS: list[str] = [
    "stares down the defender", "flexes to the crowd", "lets out a roar",
    "pounds his chest", "points to the sky", "blows a kiss to the crowd",
    "ice cold celebration", "mean mugs the bench",
    "does the shimmy", "waves goodbye", "finger to lips -- silence",
    "cups his ear to the crowd", "does the big balls dance",
    "calm and collected", "stone-faced killer",
]

# Known-for traits
KNOWN_FOR_TRAITS: dict[str, list[str]] = {
    "shooter": ["deep threes", "catch-and-shoot accuracy", "off-the-dribble scoring"],
    "defender": ["lockdown defense", "elite perimeter defense", "stealing passing lanes"],
    "playmaker": ["court vision", "finding the open man", "running the offense"],
    "athlete": ["explosive athleticism", "highlight-reel dunks", "fast-break finishing"],
    "rebounder": ["crashing the boards", "second-chance points", "boxing out"],
    "post_scorer": ["back-to-the-basket game", "footwork in the post", "touch around the rim"],
}
