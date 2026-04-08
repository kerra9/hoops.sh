"""HoopsApp - Textual App subclass with screen routing."""

from __future__ import annotations

from textual.app import App
from textual.binding import Binding


class HoopsApp(App):
    """The hoops.sh TUI application.

    Terminal-native basketball simulation interface built with Textual.
    """

    TITLE = "hoops.sh"
    SUB_TITLE = "Maximum Fidelity Basketball Simulator"
    CSS_PATH = "styles.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("question_mark", "help", "Help", show=True),
    ]

    def on_mount(self) -> None:
        """Push the main menu screen on startup."""
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self.push_screen(MainMenuScreen())

    def action_help(self) -> None:
        """Show keyboard shortcuts."""
        self.notify("Press ? for help, q to quit", title="Keyboard Shortcuts")
