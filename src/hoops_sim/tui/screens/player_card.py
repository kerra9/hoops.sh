"""Player Card screen -- deep dive on a single player.

Redesigned with dense layout, spatial shooting chart, tendency bars,
compact badges, and personality trait bars.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.models.player import Player
from hoops_sim.tui.theme import energy_color, rating_color
from hoops_sim.tui.widgets.attribute_radar import AttributeRadar
from hoops_sim.tui.widgets.badge_grid import BadgeGrid
from hoops_sim.tui.widgets.court_shooting_chart import CourtShootingChart
from hoops_sim.tui.widgets.tendency_bars import TendencyBars


class PlayerCardScreen(Screen):
    """Deep dive on a single Player.

    Dense layout with:
    - Compact header (all bio info on one line)
    - Attribute bars with color gradient
    - Spatial shooting chart
    - Compact badge grid
    - Tendency bars
    - Personality trait bars
    - Energy + morale gauges
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
            # Dense header
            height_ft = p.body.height_inches // 12
            height_in = p.body.height_inches % 12
            ovr_color = rating_color(p.overall)
            with Vertical(id="player-card-header"):
                yield Label(
                    f"[bold]#{p.jersey_number} {p.full_name}[/]  |  "
                    f"{p.position.value}  |  "
                    f"OVR: [{ovr_color}]{p.overall}[/]"
                )
                yield Label(
                    f"Age: {p.age}  "
                    f"{height_ft}'{height_in}\"  "
                    f"{p.body.weight_lbs} lbs  "
                    f"Wingspan: {p.body.wingspan_inches}\"  "
                    f"{p.body.handedness.value[0].upper()}"
                )

            yield Button("< Back", id="btn-back", classes="back-button")

            with Horizontal(id="player-card-body"):
                # Left column: attributes and badges
                with Vertical(id="player-card-left"):
                    yield Label("[bold]ATTRIBUTES[/]")
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

                    yield Label("")
                    yield Label("[bold]BADGES[/]")
                    yield BadgeGrid(badges=p.badges.badges, id="player-badges")

                    yield Label("")
                    yield Label("[bold]TENDENCIES[/]")
                    tendencies = {
                        "3PT Freq": getattr(p.tendencies, "three_point_frequency", 30.0),
                        "Mid Freq": getattr(p.tendencies, "midrange_frequency", 20.0),
                        "Drive Freq": getattr(p.tendencies, "drive_frequency", 35.0),
                        "Post Freq": getattr(p.tendencies, "post_frequency", 15.0),
                    }
                    yield TendencyBars(tendencies=tendencies, id="player-tendencies")

                # Right column: shooting chart, personality, energy
                with Vertical(id="player-card-right"):
                    yield Label("[bold]SHOOTING CHART[/]")
                    yield CourtShootingChart(
                        profile=p.shooting_profile, id="player-shooting"
                    )

                    yield Label("")
                    yield Label("[bold]PERSONALITY[/]")
                    traits = {
                        "Competitive": p.personality.competitiveness * 100,
                        "Professional": p.personality.professionalism * 100,
                        "Loyalty": p.personality.loyalty * 100,
                        "Media Savvy": p.personality.media_savvy * 100,
                    }
                    yield TendencyBars(tendencies=traits, id="player-personality")

                    yield Label("")
                    yield Label("[bold]CONDITION[/]")
                    e_color = energy_color(p.current_energy / 100.0)
                    e_bar = int(p.current_energy / 100.0 * 10)
                    e_filled = "\u2588" * e_bar
                    e_empty = "\u2591" * (10 - e_bar)
                    yield Label(
                        f"  Energy:  [{e_color}]{e_filled}{e_empty}[/] {p.current_energy:.0f}%"
                    )
                    m_bar = int(p.current_morale * 10)
                    m_filled = "\u2588" * m_bar
                    m_empty = "\u2591" * (10 - m_bar)
                    yield Label(
                        f"  Morale:  [#3498db]{m_filled}{m_empty}[/] {p.current_morale:.0%}"
                    )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
