"""Main menu screen -- entry point for the TUI.

Redesigned with figlet-style banner, hotkey grid, and recent save panel.
"""

from __future__ import annotations

from hoops_sim.tui.base import Screen, console
from hoops_sim.tui.theme import BANNER_GRADIENT

# Figlet-style banner with gradient coloring
_BANNER = r"""
 _                            _
| |__   ___   ___  _ __  ___ | |
| '_ \ / _ \ / _ \| '_ \/ __|| |
| | | | (_) | (_) | |_) \__ \|_|
|_| |_|\___/ \___/| .__/|___/(_)
                   |_|       .sh
"""


def _gradient_banner() -> str:
    """Apply gradient coloring to the banner text."""
    lines = _BANNER.strip().split("\n")
    colored_lines = []
    for i, line in enumerate(lines):
        color = BANNER_GRADIENT[i % len(BANNER_GRADIENT)]
        colored_lines.append(f"[{color}]{line}[/]")
    return "\n".join(colored_lines)


class MainMenuScreen(Screen):
    """Entry point. New season, load, quick game, settings, quit.

    Features:
    - Gradient-colored figlet banner
    - Hotkey grid instead of stacked buttons
    - Keyboard-first navigation
    """

    BINDINGS = [
        ("n", "new_season", "New Season"),
        ("g", "quick_game", "Quick Game"),
        ("s", "settings", "Settings"),
        ("q", "quit", "Quit"),
    ]

    def render(self) -> str:
        return (
            f"{_gradient_banner()}\n"
            "Maximum Fidelity Basketball Simulator\n\n"
            "  [bold green][N][/] New Season    "
            "[bold blue][G][/] Quick Game\n"
            "  [bold yellow][S][/] Settings      "
            "[bold red][Q][/] Quit\n"
        )

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "n":
            self.action_new_season()
        elif c == "g":
            self.action_quick_game()
        elif c == "s":
            self.action_settings()
        elif c == "q":
            self.action_quit()

    def action_new_season(self) -> None:
        from hoops_sim.tui.screens.season_setup import SeasonSetupScreen

        self.app.push_screen(SeasonSetupScreen())

    def action_quick_game(self) -> None:
        from hoops_sim.data.generator import generate_league
        from hoops_sim.tui.screens.live_game import LiveGameScreen
        from hoops_sim.utils.rng import SeededRNG

        rng = SeededRNG()
        league = generate_league(num_teams=2, rng=rng)
        home = league.teams[0]
        away = league.teams[1]
        self.app.push_screen(
            LiveGameScreen(
                home_team=home, away_team=away, seed=rng.randint(1, 999999)
            )
        )

    def action_settings(self) -> None:
        from hoops_sim.tui.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_quit(self) -> None:
        self.app.exit()
