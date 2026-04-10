"""Pass type templates -- per pass type with context variants."""

from __future__ import annotations

CHEST_PASS_TEMPLATES = [
    "{passer} swings it to {receiver} on the wing.",
    "{passer} finds {receiver} with a quick chest pass.",
    "{passer} moves the ball to {receiver}.",
    "Ball goes from {passer} to {receiver}.",
    "{passer} hits {receiver} with the pass.",
]

BOUNCE_PASS_TEMPLATES = [
    "{passer} threads a bounce pass to {receiver} in the post.",
    "{passer} sneaks a bounce pass to {receiver}.",
    "Nice bounce pass from {passer}! {receiver} has it.",
    "{passer} feeds {receiver} with the bounce pass.",
]

LOB_PASS_TEMPLATES = [
    "{passer} lobs it in to {receiver}!",
    "{passer} throws the lob... {receiver} catches it high!",
    "Lob pass from {passer} to {receiver} near the basket!",
]

BULLET_PASS_TEMPLATES = [
    "{passer} fires a bullet pass across to {receiver}!",
    "{passer} zips it to {receiver}! Quick hands!",
    "Bullet pass from {passer}! {receiver} catches it in stride.",
]

OVERHEAD_PASS_TEMPLATES = [
    "{passer} throws the overhead pass to {receiver}.",
    "{passer} with the overhead feed to {receiver}.",
]

ENTRY_PASS_TEMPLATES = [
    "{passer} feeds the post. {receiver} has position.",
    "{passer} gets the entry pass into {receiver} on the block.",
    "{passer} throws it in to {receiver} down low.",
    "Entry pass from {passer} to {receiver} in the post.",
]

SKIP_PASS_TEMPLATES = [
    "{passer} skips it across to {receiver} on the far side!",
    "Skip pass from {passer}! {receiver} is wide open on the wing!",
    "{passer} swings it all the way to {receiver}! Ball reversal!",
    "{passer} fires the skip pass to {receiver} in the corner!",
]

KICK_OUT_TEMPLATES = [
    "{passer} kicks it out to {receiver} on the perimeter!",
    "{passer} drives and dishes to {receiver}!",
    "Kick-out pass from {passer}! {receiver} catches and...",
    "{passer} finds {receiver} on the kick-out!",
    "{passer} draws the help and kicks it to {receiver}!",
]

HOCKEY_ASSIST_TEMPLATES = [
    "The extra pass! {passer} moves it to {receiver}!",
    "{passer} makes the hockey assist to {receiver}!",
    "Unselfish play by {passer}, finds {receiver} for the better look.",
]

DIME_TEMPLATES = [
    "What a pass by {passer}! Threading the needle to {receiver}!",
    "Dime from {passer}! {receiver} has an easy look!",
    "{passer} with the vision! Finds {receiver} cutting to the basket!",
    "Beautiful find by {passer}! {receiver} catches it in rhythm!",
]

PASS_TEMPLATES_BY_TYPE = {
    "chest": CHEST_PASS_TEMPLATES,
    "bounce": BOUNCE_PASS_TEMPLATES,
    "lob": LOB_PASS_TEMPLATES,
    "bullet": BULLET_PASS_TEMPLATES,
    "overhead": OVERHEAD_PASS_TEMPLATES,
}
