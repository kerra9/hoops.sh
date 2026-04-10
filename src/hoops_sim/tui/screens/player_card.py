"""Player Card screen -- deep dive on a single player.

Textual Screen with attribute visualization, badges, and shooting chart.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from hoops_sim.models.player import Player
from hoops_sim.tui.theme import energy_color, rating_color
from hoops_sim.tui.widgets.attribute_radar import AttributeRadar
from hoops_sim.tui.widgets.badge_grid import BadgeGrid
from hoops_sim.tui.widgets.court_shooting_chart import CourtShootingChart
from hoops_sim.tui.widgets.tendency_bars import TendencyBars


class PlayerCardScreen(Screen):
    """Deep dive on a single Player."""

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
        Binding("b", "go_back", "Back"),
    ]

    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player

    def compose(self) -> ComposeResult:
        p = self.player
        height_ft = p.body.height_inches // 12
        height_in = p.body.height_inches % 12
        ovr_color = rating_color(p.overall)

        yield Header()
        with VerticalScroll(id="player-card"):
            yield Static(
                f"[bold]#{p.jersey_number} {p.full_name}[/]  |  "
                f"{p.position.value}  |  "
                f"OVR: [{ovr_color}]{p.overall}[/]\n"
                f"Age: {p.age}  "
                f"{height_ft}'{height_in}\"  "
                f"{p.body.weight_lbs} lbs  "
                f"Wingspan: {p.body.wingspan_inches}\"  "
                f"{p.body.handedness.value[0].upper()}",
                markup=True,
                classes="player-header",
            )

            # Attributes
            yield Static("[bold]ATTRIBUTES[/]", markup=True)
            categories = {
                "Shooting": p.attributes.shooting_avg(),
                "Finishing": p.attributes.finishing_avg(),
                "Playmaking": p.attributes.playmaking_avg(),
                "Defense": p.attributes.defense_avg(),
                "Rebounding": p.attributes.rebounding_avg(),
                "Athleticism": p.attributes.athleticism_avg(),
                "Mental": p.attributes.mental_avg(),
            }
            yield AttributeRadar(categories=categories, classes="player-attributes")

            # Badges
            yield Static("[bold]BADGES[/]", markup=True)
            yield BadgeGrid(badges=p.badges.badges, classes="player-badges")

            # Tendencies
            yield Static("[bold]TENDENCIES[/]", markup=True)
            tendencies = {
                "3PT Freq": getattr(p.tendencies, "three_point_frequency", 30.0),
                "Mid Freq": getattr(p.tendencies, "midrange_frequency", 20.0),
                "Drive Freq": getattr(p.tendencies, "drive_frequency", 35.0),
                "Post Freq": getattr(p.tendencies, "post_frequency", 15.0),
            }
            yield TendencyBars(tendencies=tendencies, classes="player-tendencies")

            # Shooting chart
            yield Static("[bold]SHOOTING CHART[/]", markup=True)
            yield CourtShootingChart(profile=p.shooting_profile)

            # Personality
            yield Static("[bold]PERSONALITY[/]", markup=True)
            traits = {
                "Competitive": p.personality.competitiveness * 100,
                "Professional": p.personality.professionalism * 100,
                "Loyalty": p.personality.loyalty * 100,
                "Media Savvy": p.personality.media_savvy * 100,
            }
            yield TendencyBars(tendencies=traits)

            # Condition
            yield Static("[bold]CONDITION[/]", markup=True)
            e_pct = p.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 10)
            e_filled = "\u2588" * e_bar
            e_empty = "\u2591" * (10 - e_bar)
            m_bar = int(p.current_morale * 10)
            m_filled = "\u2588" * m_bar
            m_empty = "\u2591" * (10 - m_bar)
            yield Static(
                f"  Energy:  [{e_color}]{e_filled}{e_empty}[/] {p.current_energy:.0f}%\n"
                f"  Morale:  [#3498db]{m_filled}{m_empty}[/] {p.current_morale:.0%}",
                markup=True,
                classes="player-condition",
            )
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()
