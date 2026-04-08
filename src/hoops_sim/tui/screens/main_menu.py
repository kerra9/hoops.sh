"""Main menu screen -- entry point for the TUI."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label


class MainMenuScreen(Screen):
    """Entry point. New season, load, quick game, settings, quit."""

    BINDINGS = [
        ("n", "new_season", "New Season"),
        ("g", "quick_game", "Quick Game"),
        ("s", "settings", "Settings"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="main-menu"):
            with Vertical(id="main-menu-buttons"):
                yield Label(
                    r"""
 _                            _
| |__   ___   ___  _ __  ___ | |
| '_ \ / _ \ / _ \| '_ \/ __|| |
| | | | (_) | (_) | |_) \__ \|_|
|_| |_|\___/ \___/| .__/|___/(_)
                   |_|       .sh
""",
                    id="main-menu-title",
                )
                yield Label(
                    "Maximum Fidelity Basketball Simulator",
                    id="main-menu-subtitle",
                )
                yield Button("New Season", id="btn-new-season", variant="primary")
                yield Button("Quick Game", id="btn-quick-game", variant="default")
                yield Button("Settings", id="btn-settings", variant="default")
                yield Button("Quit", id="btn-quit", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-new-season":
            self.action_new_season()
        elif event.button.id == "btn-quick-game":
            self.action_quick_game()
        elif event.button.id == "btn-settings":
            self.action_settings()
        elif event.button.id == "btn-quit":
            self.app.exit()

    def action_new_season(self) -> None:
        from hoops_sim.tui.screens.season_setup import SeasonSetupScreen

        self.app.push_screen(SeasonSetupScreen())

    def action_quick_game(self) -> None:
        from hoops_sim.data.generator import generate_league
        from hoops_sim.tui.screens.live_game import LiveGameScreen
        from hoops_sim.utils.rng import SeededRNG

        # Generate two random teams for a quick game
        rng = SeededRNG()
        league = generate_league(num_teams=2, rng=rng)
        home = league.teams[0]
        away = league.teams[1]
        self.app.push_screen(
            LiveGameScreen(home_team=home, away_team=away, seed=rng.randint(1, 999999))
        )

    def action_settings(self) -> None:
        from hoops_sim.tui.screens.settings import SettingsScreen

        self.app.push_screen(SettingsScreen())

    def action_quit(self) -> None:
        self.app.exit()
