"""HoopsApp -- Textual App with screen routing and CSS theming.

The main entry point for the hoops.sh TUI, built on Textual for
async rendering, CSS styling, mouse support, and real widget composition.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header


class HoopsApp(App):
    """The hoops.sh TUI application.

    Textual-native basketball simulation interface with async game
    simulation, CSS-styled widgets, and screen-based navigation.
    """

    TITLE = "hoops.sh"
    SUB_TITLE = "Maximum Fidelity Basketball Simulator"

    CSS_PATH = [
        "styles/base.tcss",
        "styles/screens.tcss",
        "styles/widgets.tcss",
        "styles/scoreboard.tcss",
        "styles/court.tcss",
        "styles/tables.tcss",
        "styles/cards.tcss",
    ]

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True, priority=True),
        Binding("d", "toggle_dark", "Dark Mode", show=True),
        Binding("question_mark", "help", "Help", show=True),
    ]

    ENABLE_COMMAND_PALETTE = False

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Push the main menu screen on app start."""
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self.push_screen(MainMenuScreen())

    def action_help(self) -> None:
        """Show help overlay."""
        from hoops_sim.tui.screens.help import HelpScreen

        self.push_screen(HelpScreen())
