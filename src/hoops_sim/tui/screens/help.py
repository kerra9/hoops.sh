"""Help overlay screen.

Textual Screen showing keyboard shortcuts and navigation help.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, Static


class HelpScreen(ModalScreen):
    """Help overlay showing keyboard shortcuts."""

    BINDINGS = [
        Binding("escape", "dismiss", "Close", show=True),
        Binding("question_mark", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Static(
                "[bold]hoops.sh -- Keyboard Shortcuts[/]\n\n"
                "[bold]Global[/]\n"
                "  [bold green]q[/]       Quit / Back\n"
                "  [bold green]?[/]       This help screen\n"
                "  [bold green]d[/]       Toggle dark/light mode\n"
                "  [bold green]Escape[/]  Pop screen / close overlay\n"
                "  [bold green]Tab[/]     Next focus\n\n"
                "[bold]Main Menu[/]\n"
                "  [bold green]n[/]  New Season\n"
                "  [bold green]g[/]  Quick Game\n"
                "  [bold green]s[/]  Settings\n\n"
                "[bold]League Hub[/]\n"
                "  [bold green]t[/]  Team Dashboard\n"
                "  [bold green]s[/]  Standings\n"
                "  [bold green]c[/]  Schedule\n"
                "  [bold green]a[/]  Advance Day\n"
                "  [bold green]p[/]  Play Next Game\n\n"
                "[bold]Live Game[/]\n"
                "  [bold green]Space[/]  Pause/Resume\n"
                "  [bold green]f[/]      Fast Forward\n"
                "  [bold green]s[/]      Slow Down\n"
                "  [bold green]i[/]      Instant Sim\n"
                "  [bold green]b[/]      Box Score\n",
                markup=True,
            )
            yield Button("Close", variant="primary", id="btn-close")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-close":
            self.dismiss()

    def action_dismiss(self) -> None:
        self.dismiss()
