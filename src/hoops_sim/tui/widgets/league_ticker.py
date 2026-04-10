"""Horizontally scrolling recent game results ticker."""

from __future__ import annotations

from typing import List

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label


class LeagueTicker(Widget):
    """Scrolling ticker of recent game results.

    Shows completed game scores in a compact horizontal format.
    """

    DEFAULT_CSS = """
    LeagueTicker {
        height: auto;
        width: 100%;
    }
    """

    def __init__(
        self,
        results: List[str] | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._results = results or []

    def compose(self) -> ComposeResult:
        yield Label("[bold]LEAGUE TICKER[/]")
        if self._results:
            for result in self._results[:5]:
                yield Label(f"  {result}")
        else:
            yield Label("  [dim]No recent games[/]")

    def update_results(self, results: List[str]) -> None:
        """Update the ticker results."""
        self._results = results
        self.refresh(recompose=True)
