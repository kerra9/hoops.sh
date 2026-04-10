"""Roster Management screen -- lineup ordering, starter/bench assignment."""

from __future__ import annotations

from hoops_sim.models.team import Team
from hoops_sim.tui.base import Screen
from hoops_sim.tui.theme import energy_color


class RosterManagementScreen(Screen):
    """Lineup ordering, starter/bench assignment."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self, team: Team) -> None:
        super().__init__()
        self.team = team

    def render(self) -> str:
        lines = [
            f"[bold]{self.team.full_name} -- Roster Management[/]",
            "",
        ]

        starters = self.team.get_starters()
        starter_ids = {p.id for p in starters}
        bench = [p for p in self.team.roster if p.id not in starter_ids]

        header = f"{'#':>3} {'Name':<22} {'Pos':<4} {'OVR':>3} {'Age':>3} Energy"

        # Starters
        lines.append("[bold green]STARTERS[/]")
        lines.append(header)
        for p in starters:
            e_pct = p.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 5)
            filled = "\u2588" * e_bar
            empty = "\u2591" * (5 - e_bar)
            energy_str = f"[{e_color}]{filled}{empty}[/]"
            lines.append(
                f"{p.jersey_number:>3} {p.full_name:<22} {p.position.value:<4} "
                f"{p.overall:>3} {p.age:>3} {energy_str}"
            )

        lines.append("")

        # Bench
        lines.append("[bold yellow]BENCH[/]")
        lines.append(header)
        for p in sorted(bench, key=lambda x: x.overall, reverse=True):
            e_pct = p.current_energy / 100.0
            e_color = energy_color(e_pct)
            e_bar = int(e_pct * 5)
            filled = "\u2588" * e_bar
            empty = "\u2591" * (5 - e_bar)
            energy_str = f"[{e_color}]{filled}{empty}[/]"
            lines.append(
                f"{p.jersey_number:>3} {p.full_name:<22} {p.position.value:<4} "
                f"{p.overall:>3} {p.age:>3} {energy_str}"
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
