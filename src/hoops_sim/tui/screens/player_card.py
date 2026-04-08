"""Player Card screen -- deep dive on a single player."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.models.player import Player
from hoops_sim.tui.widgets.attribute_radar import AttributeRadar
from hoops_sim.tui.widgets.badge_grid import BadgeGrid
from hoops_sim.tui.widgets.shooting_chart import ShootingChart


class PlayerCardScreen(Screen):
    """Deep dive on a single Player.

    Shows attributes radar, badges, shooting profile heatmap,
    tendencies, body stats.
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player

    def compose(self) -> ComposeResult:
        p = self.player
        yield Header()
        with Vertical(id="player-card"):
            # Header section
            height_ft = p.body.height_inches // 12
            height_in = p.body.height_inches % 12
            with Vertical(id="player-card-header"):
                yield Label(
                    f"#{p.jersey_number} {p.full_name}  "
                    f"{p.position.value}  "
                    f"OVR: {p.overall}"
                )
                yield Label(
                    f"Age: {p.age}  "
                    f"{height_ft}'{height_in}\"  "
                    f"{p.body.weight_lbs} lbs  "
                    f"Wingspan: {p.body.wingspan_inches}\"  "
                    f"{p.body.handedness.value}-handed"
                )

            yield Button("< Back", id="btn-back", classes="back-button")

            with Horizontal(id="player-card-body"):
                # Left column: attributes and badges
                with Vertical(id="player-card-left"):
                    yield Label("Attributes", classes="conference-header")
                    categories = {
                        "Shooting": p.attributes.shooting_avg(),
                        "Finishing": p.attributes.finishing_avg(),
                        "Playmaking": p.attributes.playmaking_avg(),
                        "Defense": p.attributes.defense_avg(),
                        "Rebounding": p.attributes.rebounding_avg(),
                        "Athleticism": p.attributes.athleticism_avg(),
                        "Mental": p.attributes.mental_avg(),
                    }
                    yield AttributeRadar(categories=categories, id="player-radar")

                    yield Label("Badges", classes="conference-header")
                    yield BadgeGrid(badges=p.badges.badges, id="player-badges")

                # Right column: shooting chart and personality
                with Vertical(id="player-card-right"):
                    yield Label("Shooting Zones", classes="conference-header")
                    yield ShootingChart(profile=p.shooting_profile, id="player-zones")

                    yield Label("Personality", classes="conference-header")
                    yield Label(
                        f"  Competitiveness: {p.personality.competitiveness:.0%}\n"
                        f"  Professionalism: {p.personality.professionalism:.0%}\n"
                        f"  Loyalty: {p.personality.loyalty:.0%}\n"
                        f"  Media Savvy: {p.personality.media_savvy:.0%}"
                    )

                    yield Label("Energy", classes="conference-header")
                    yield Label(f"  Current: {p.current_energy:.0f}%")
                    yield Label(f"  Morale: {p.current_morale:.0%}")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
