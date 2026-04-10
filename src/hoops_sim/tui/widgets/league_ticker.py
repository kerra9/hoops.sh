"""Horizontally scrolling recent game results ticker."""

from __future__ import annotations

from typing import List

from hoops_sim.tui.base import Widget


class LeagueTicker(Widget):
    """Scrolling ticker of recent game results."""

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

    def render(self) -> str:
        lines = ["[bold]LEAGUE TICKER[/]"]
        if self._results:
            for result in self._results[:5]:
                lines.append(f"  {result}")
        else:
            lines.append("  [dim]No recent games[/]")
        return "\n".join(lines)

    def update_results(self, results: List[str]) -> None:
        """Update the ticker results."""
        self._results = results
