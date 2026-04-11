"""Clause bank for setup events: ball advance, probing, jab steps."""

from hoops_sim.narration.clause_banks import ClauseBank

BALL_ADVANCE: ClauseBank = {
    "walk_it_up": {
        "calm": [
            "brings the ball up the court",
            "walks it up slowly",
            "brings it across halfcourt",
            "dribbles up the floor",
            "takes his time coming up the court",
            "crosses halfcourt with a slow dribble",
            "brings the ball up the court with a slow dribble",
            "advances the ball up the floor",
        ],
        "building": [
            "brings the ball up... surveying the defense",
            "crosses halfcourt, looking for an opening",
            "brings it up, calling out the play",
            "dribbles up... sizing up the defense",
            "walks it up, takes a look at the shot clock",
            "brings the ball up the court, setting up the offense",
            "takes his time... reading the defense",
            "brings it across, directing traffic",
        ],
        "hype": [
            "brings it up quickly! Looking to attack!",
            "pushes it up the floor!",
            "races up the court!",
            "brings it up with urgency!",
            "pushes the pace!",
            "up the floor quickly, looking for an opening!",
            "brings it up with purpose!",
            "hustles up the court!",
        ],
        "screaming": [
            "PUSHES IT UP THE FLOOR!",
            "RACES UP THE COURT!",
            "UP THE FLOOR IN A HURRY!",
            "BRINGS IT UP! NO TIME TO WASTE!",
            "PUSHING THE PACE!",
            "FLIES UP THE COURT!",
            "UP THE FLOOR! CLOCK IS TICKING!",
            "SPRINTS UP THE COURT!",
        ],
    },
    "transition": {
        "calm": [
            "pushes it in transition",
            "gets out on the fast break",
            "leads the break",
            "pushing the pace",
        ],
        "building": [
            "pushes it in transition... numbers advantage",
            "leads the fast break... looking ahead",
            "on the run... has numbers",
            "pushing the pace! Outlet and go!",
        ],
        "hype": [
            "TRANSITION! Numbers advantage!",
            "on the break! Here we go!",
            "pushes it! Fast break opportunity!",
            "leads the break! Wide open court ahead!",
        ],
        "screaming": [
            "FAST BREAK! HERE WE GO!",
            "ON THE RUN! CAN'T STOP THIS!",
            "TRANSITION! OPEN COURT!",
            "PUSHING IT! THE DEFENSE CAN'T GET BACK!",
        ],
    },
}

PROBING: ClauseBank = {
    "probing": {
        "calm": [
            "sizes up the defense",
            "jab step, feeling out {defender}",
            "probing the defense",
            "looking for an opening",
            "dribbles in place, reading the defense",
            "surveys the floor",
            "patient with the ball",
            "waits for something to develop",
        ],
        "building": [
            "jab step... {defender} doesn't bite",
            "sizes up {defender}... looking for a way in",
            "probing... waiting for the right moment",
            "triple threat, jab step at {defender}",
            "feeling out {defender}... looking for a crease",
            "working the ball, looking for his spot",
            "jab, jab... {defender} stays disciplined",
            "sizing up {defender}... measuring the distance",
        ],
        "hype": [
            "jab step! {defender} flinches!",
            "sizes up {defender}! Here it comes!",
            "probing... about to make his move!",
            "reading {defender} like a book!",
        ],
        "screaming": [
            "STARING DOWN {DEFENDER}!",
            "JAB STEP! {DEFENDER} IS SHOOK!",
            "SIZING HIM UP! HERE IT COMES!",
            "READING THE DEFENSE! ABOUT TO GO!",
        ],
    },
}


def get_setup_clauses(
    setup_type: str, band: str,
) -> list[str]:
    """Get setup clauses at an intensity band."""
    if setup_type in BALL_ADVANCE:
        return BALL_ADVANCE[setup_type].get(
            band, BALL_ADVANCE[setup_type]["calm"],
        )
    if setup_type in PROBING:
        return PROBING[setup_type].get(
            band, PROBING[setup_type]["calm"],
        )
    # Default to walk_it_up calm
    return BALL_ADVANCE["walk_it_up"]["calm"]
