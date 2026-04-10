"""Main menu screen -- entry point for the TUI.

Textual Screen with compose() yielding Button widgets and a gradient banner.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from hoops_sim.tui.theme import BANNER_GRADIENT

# Figlet-style banner
_BANNER = r"""
 _                            _
| |__   ___   ___  _ __  ___ | |
| '_ \ / _ \ / _ \| '_ \/ __|| |
| | | | (_) | (_) | |_) \__ \|_|
|_| |_|\___/ \___/| .__/|___/(_)
                   |_|       .sh
"""


def _gradient_banner() -> str:
    """Apply gradient coloring to the banner text using Rich markup."""
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
    - Button widgets in a horizontal layout
    - Keyboard-first navigation with proper action handlers
    """

    BINDINGS = [
        Binding("n", "new_season", "New Season", show=True),
        Binding("g", "quick_game", "Quick Game", show=True),
        Binding("s", "settings", "Settings", show=True),
        Binding("q", "quit_app", "Quit", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="main-menu"):
                yield Static(_gradient_banner(), id="main-menu-banner", markup=True)
                yield Static(
                    "[dim]Maximum Fidelity Basketball Simulator[/]",
                    id="main-menu-subtitle",
                    markup=True,
                )
                with Horizontal(id="main-menu-buttons"):
                    yield Button("New Season", variant="success", id="btn-new-season")
                    yield Button("Quick Game", variant="primary", id="btn-quick-game")
                    yield Button("Settings", variant="warning", id="btn-settings")
                    yield Button("Quit", variant="error", id="btn-quit")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-new-season":
            self.action_new_season()
        elif event.button.id == "btn-quick-game":
            self.action_quick_game()
        elif event.button.id == "btn-settings":
            self.action_settings()
        elif event.button.id == "btn-quit":
            self.action_quit_app()

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

    def action_quit_app(self) -> None:
        self.app.exit()
