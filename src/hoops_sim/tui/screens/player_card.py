"""Player Card screen -- deep dive on a single player."""

from __future__ import annotations

from hoops_sim.models.player import Player
from hoops_sim.tui.base import Screen
from hoops_sim.tui.theme import energy_color, rating_color
from hoops_sim.tui.widgets.attribute_radar import AttributeRadar
from hoops_sim.tui.widgets.badge_grid import BadgeGrid
from hoops_sim.tui.widgets.court_shooting_chart import CourtShootingChart
from hoops_sim.tui.widgets.tendency_bars import TendencyBars


class PlayerCardScreen(Screen):
    """Deep dive on a single Player."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, player: Player) -> None:
        super().__init__()
        self.player = player

    def render(self) -> str:
        p = self.player
        height_ft = p.body.height_inches // 12
        height_in = p.body.height_inches % 12
        ovr_color = rating_color(p.overall)

        lines = [
            f"[bold]#{p.jersey_number} {p.full_name}[/]  |  "
            f"{p.position.value}  |  "
            f"OVR: [{ovr_color}]{p.overall}[/]",
            f"Age: {p.age}  "
            f"{height_ft}'{height_in}\"  "
            f"{p.body.weight_lbs} lbs  "
            f"Wingspan: {p.body.wingspan_inches}\"  "
            f"{p.body.handedness.value[0].upper()}",
            "",
        ]

        # Attributes
        lines.append("[bold]ATTRIBUTES[/]")
        categories = {
            "Shooting": p.attributes.shooting_avg(),
            "Finishing": p.attributes.finishing_avg(),
            "Playmaking": p.attributes.playmaking_avg(),
            "Defense": p.attributes.defense_avg(),
            "Rebounding": p.attributes.rebounding_avg(),
            "Athleticism": p.attributes.athleticism_avg(),
            "Mental": p.attributes.mental_avg(),
        }
        radar = AttributeRadar(categories=categories)
        lines.append(radar.render())
        lines.append("")

        # Badges
        lines.append("[bold]BADGES[/]")
        badges = BadgeGrid(badges=p.badges.badges)
        lines.append(badges.render())
        lines.append("")

        # Tendencies
        lines.append("[bold]TENDENCIES[/]")
        tendencies = {
            "3PT Freq": getattr(p.tendencies, "three_point_frequency", 30.0),
            "Mid Freq": getattr(p.tendencies, "midrange_frequency", 20.0),
            "Drive Freq": getattr(p.tendencies, "drive_frequency", 35.0),
            "Post Freq": getattr(p.tendencies, "post_frequency", 15.0),
        }
        tb = TendencyBars(tendencies=tendencies)
        lines.append(tb.render())
        lines.append("")

        # Shooting chart
        lines.append("[bold]SHOOTING CHART[/]")
        chart = CourtShootingChart(profile=p.shooting_profile)
        lines.append(chart.render())
        lines.append("")

        # Personality
        lines.append("[bold]PERSONALITY[/]")
        traits = {
            "Competitive": p.personality.competitiveness * 100,
            "Professional": p.personality.professionalism * 100,
            "Loyalty": p.personality.loyalty * 100,
            "Media Savvy": p.personality.media_savvy * 100,
        }
        ptb = TendencyBars(tendencies=traits)
        lines.append(ptb.render())
        lines.append("")

        # Condition
        lines.append("[bold]CONDITION[/]")
        e_color = energy_color(p.current_energy / 100.0)
        e_bar = int(p.current_energy / 100.0 * 10)
        e_filled = "\u2588" * e_bar
        e_empty = "\u2591" * (10 - e_bar)
        lines.append(
            f"  Energy:  [{e_color}]{e_filled}{e_empty}[/] {p.current_energy:.0f}%"
        )
        m_bar = int(p.current_morale * 10)
        m_filled = "\u2588" * m_bar
        m_empty = "\u2591" * (10 - m_bar)
        lines.append(
            f"  Morale:  [#3498db]{m_filled}{m_empty}[/] {p.current_morale:.0%}"
        )

        lines.append("")
        lines.append("  [bold red][B][/] Back")
        return "\n".join(lines)

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "b":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
