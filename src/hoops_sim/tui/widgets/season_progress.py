"""Season progress bar showing games played."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.tui.theme import ACCENT_SUCCESS


class SeasonProgressBar(Widget):
    """Games played progress bar.

    Shows a visual bar and fraction of games completed.
    """

    DEFAULT_CSS = """
    SeasonProgressBar {
        height: 2;
        width: 100%;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        games_played: int = 0,
        total_games: int = 82,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._games_played = games_played
        self._total_games = max(1, total_games)

    def compose(self) -> ComposeResult:
        pct = self._games_played / self._total_games
        bar_w = int(pct * 20)
        filled = "\u2588" * bar_w
        empty = "\u2591" * (20 - bar_w)
        yield Label(
            f"  [{ACCENT_SUCCESS}]{filled}[/]{empty} {pct:.0%}"
        )
        yield Label(
            f"  {self._games_played} / {self._total_games} games played"
        )

    def update_progress(self, games_played: int, total_games: int = 82) -> None:
        """Update progress bar."""
        self._games_played = games_played
        self._total_games = max(1, total_games)
        self.refresh(recompose=True)
