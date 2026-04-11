"""Clause bank for drive events."""

from hoops_sim.narration.clause_banks import ClauseBank

DRIVE_CLAUSES: ClauseBank = {
    "drive": {
        "calm": [
            "drives to the basket",
            "attacks the rim",
            "takes it to the hole",
            "drives left",
            "drives right",
            "heads to the basket",
            "pushes into the lane",
            "penetrates the defense",
        ],
        "building": [
            "drives to the left... {defender} struggling to keep up",
            "attacks the rim with authority",
            "gets into the lane... draws the help",
            "drives hard to the right... past {defender}",
            "bulldozes into the paint",
            "pushes past {defender} into the lane",
            "drives baseline... gets around {defender}",
            "takes {defender} off the dribble and drives",
        ],
        "hype": [
            "DRIVES! Gets past {defender}!",
            "ATTACKS THE RIM! {defender} can't stop him!",
            "drives and {defender} is left behind!",
            "BLOWS BY {defender} on the drive!",
            "powers into the lane! Nothing stopping him!",
            "to the basket! {defender} caught flat-footed!",
            "EXPLODES to the rim!",
            "drives through traffic! Can't be stopped!",
        ],
        "screaming": [
            "DRIVES RIGHT BY {DEFENDER}! NO CHANCE!",
            "ATTACKS THE RIM! GET OUT OF THE WAY!",
            "BLOWS PAST {DEFENDER}! TOO FAST! TOO STRONG!",
            "EXPLODES TO THE BASKET! UNSTOPPABLE!",
            "DRIVES WITH AUTHORITY! {DEFENDER} IS LEFT IN THE DUST!",
            "TO THE RIM! {DEFENDER} HAD ABSOLUTELY NO ANSWER!",
            "STRAIGHT TO THE BASKET! NOTHING {DEFENDER} CAN DO!",
            "POWERS THROUGH! {DEFENDER} MIGHT AS WELL NOT BE THERE!",
        ],
    },
}


def get_drive_clauses(band: str) -> list[str]:
    """Get drive clauses at an intensity band."""
    return DRIVE_CLAUSES["drive"].get(band, DRIVE_CLAUSES["drive"]["calm"])
