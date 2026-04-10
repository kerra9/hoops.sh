"""Settings screen for sim speed, narration verbosity, display preferences."""

from __future__ import annotations

from hoops_sim.tui.base import Screen


class SettingsScreen(Screen):
    """Settings for sim speed and display preferences."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._sim_speed = 100
        self._narration = "normal"
        self._auto_save = True

    def render(self) -> str:
        return (
            "[bold]Settings[/]\n\n"
            "[bold green]SIMULATION[/]\n"
            f"  Sim Speed (ms between ticks): {self._sim_speed}\n"
            "  Options: 0 (Instant), 50 (Fast), 100 (Normal), 250 (Slow), 500 (Very Slow)\n\n"
            "[bold blue]DISPLAY[/]\n"
            f"  Narration Verbosity: {self._narration}\n\n"
            "[bold yellow]AUTO-SAVE[/]\n"
            f"  Auto-save after each game: {'On' if self._auto_save else 'Off'}\n\n"
            "  [bold red][B][/] Back\n"
        )

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "b":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
