"""Voice profiles for announcer personalities."""

from hoops_sim.narration.voice import AnnouncerProfile


def classic_profile() -> AnnouncerProfile:
    """Balanced, professional broadcast voice."""
    return AnnouncerProfile(
        name="Classic",
        style="balanced",
        caps_threshold=0.85,
        exclamation_density=0.5,
        ellipsis_love=0.4,
        verbosity=0.5,
        defender_focus=0.5,
        crowd_awareness=0.3,
        preferred_clause_length="medium",
        sentence_rhythm="mixed",
    )


def hype_profile() -> AnnouncerProfile:
    """Maximum energy, Kevin Harlan-style voice."""
    return AnnouncerProfile(
        name="Hype",
        style="dramatic",
        three_pointer_calls=[
            "BANG!", "BANG! BANG!", "FROM DEEEP!", "SPLASH FROM DOWNTOWN!",
            "ARE YOU KIDDING ME?!", "HE'S ON FIRE!",
        ],
        dunk_calls=[
            "WITH NO REGARD FOR HUMAN LIFE!",
            "LOOK AT THIS MAN!", "OH MY!",
            "THROWS IT DOWN WITH AUTHORITY!",
            "POSTER! ABSOLUTE POSTER!",
        ],
        ankle_breaker_calls=[
            "BROKE HIS ANKLES!", "SENT HIM TO THE SHADOW REALM!",
            "OH MY GOODNESS!", "SOMEBODY CALL 911!",
            "THAT MAN HAD A FAMILY!",
        ],
        block_calls=[
            "GET THAT OUTTA HERE!", "REJECTED!",
            "NOT IN MY HOUSE!", "SWATTED INTO THE STANDS!",
        ],
        general_reactions=[
            "ARE YOU KIDDING ME?!", "LOOK AT THIS!",
            "OH! MY! GOODNESS!", "WHAT DID WE JUST WITNESS?!",
            "I CANNOT BELIEVE IT!", "SOMEBODY STOP HIM!",
        ],
        staredown_phrases=[
            "STARES HIM DOWN! ICE IN HIS VEINS!",
            "THE STAREDOWN! THE DISRESPECT!",
            "LOOKS RIGHT AT HIM! COLD-BLOODED!",
        ],
        separation_phrases=[
            "LOOK AT THIS SEPARATION!",
            "ACRES OF SPACE! ALL ALONE!",
            "NOBODY WITHIN 10 FEET!",
        ],
        crowd_references=[
            "THE CROWD IS GOING ABSOLUTELY INSANE!",
            "LISTEN TO THIS BUILDING! DEAFENING!",
            "THE ARENA IS SHAKING!",
            "I CAN'T EVEN HEAR MYSELF THINK!",
        ],
        caps_threshold=0.7,
        exclamation_density=0.8,
        ellipsis_love=0.3,
        verbosity=0.6,
        defender_focus=0.7,
        crowd_awareness=0.6,
        preferred_clause_length="short",
        sentence_rhythm="staccato",
    )


def radio_profile() -> AnnouncerProfile:
    """Descriptive, spatial, verbose radio-style voice."""
    return AnnouncerProfile(
        name="Radio",
        style="analytical",
        three_pointer_calls=[
            "And it goes!", "Got it! Three-pointer!", "From downtown, good!",
        ],
        dunk_calls=[
            "Throws it down with two hands!", "A powerful slam!",
            "And he dunks it home!",
        ],
        general_reactions=[
            "What a play!", "Outstanding!", "Tremendous!",
        ],
        crowd_references=[
            "the crowd appreciates that one",
            "the fans are into this game",
            "you can feel the energy in the building",
        ],
        caps_threshold=0.9,
        exclamation_density=0.3,
        ellipsis_love=0.5,
        verbosity=0.8,
        defender_focus=0.4,
        crowd_awareness=0.4,
        preferred_clause_length="long",
        sentence_rhythm="flowing",
    )


def old_school_profile() -> AnnouncerProfile:
    """Understated, Marv Albert-style voice."""
    return AnnouncerProfile(
        name="OldSchool",
        style="poetic",
        three_pointer_calls=[
            "Yes!", "From downtown!", "A spectacular shot!",
        ],
        dunk_calls=[
            "A spectacular dunk!", "Throws it down!",
            "With the facial!",
        ],
        general_reactions=[
            "Yes!", "A spectacular move!",
            "What a play by the young man!",
        ],
        crowd_references=[
            "the crowd rises to its feet",
            "a standing ovation",
        ],
        caps_threshold=0.9,
        exclamation_density=0.4,
        ellipsis_love=0.5,
        verbosity=0.5,
        defender_focus=0.3,
        crowd_awareness=0.2,
        preferred_clause_length="medium",
        sentence_rhythm="flowing",
    )


# All available profiles
VOICE_PROFILES = {
    "classic": classic_profile,
    "hype": hype_profile,
    "radio": radio_profile,
    "old_school": old_school_profile,
}
