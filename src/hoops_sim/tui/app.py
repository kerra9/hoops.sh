"""HoopsApp - Rich-only App with screen routing."""

from __future__ import annotations

from hoops_sim.tui.base import App


class HoopsApp(App):
    """The hoops.sh TUI application.

    Terminal-native basketball simulation interface built with Rich.
    """

    TITLE = "hoops.sh"
    SUB_TITLE = "Maximum Fidelity Basketball Simulator"

    def run(self) -> None:
        """Run the application with a Rich console input loop."""
        from hoops_sim.tui.base import console
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self._running = True
        screen = MainMenuScreen()
        screen.app = self
        self._screen_stack = [screen]

        while self._running and self._screen_stack:
            current = self._screen_stack[-1]
            current.app = self

            console.clear()
            console.print(f"[bold]{self.TITLE}[/] -- {self.SUB_TITLE}\n")
            rendered = current.render()
            if rendered:
                console.print(rendered)

            try:
                choice = console.input("\n[dim]> [/]")
            except (EOFError, KeyboardInterrupt):
                break

            if hasattr(current, "handle_input"):
                current.handle_input(choice)
