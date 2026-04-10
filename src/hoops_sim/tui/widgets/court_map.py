"""ASCII half-court renderer with player positions, ball, and zones.

The crown jewel widget: renders a half-court using box-drawing and
Unicode characters with player positions from CourtState.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from textual.app import ComposeResult
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static

from hoops_sim.tui.theme import COURT_LINES, HOT_ZONE, NEUTRAL_ZONE, PAINT

# Half-court dimensions in characters
COURT_W = 34
COURT_H = 16

# Blank court template (half-court, basket at bottom)
_BLANK_COURT = [
    " +--------------------------------+",
    " /                                \\",
    "/    .         .         .          \\",
    "|                                    |",
    "|         +-----------+              |",
    "|         |           |              |",
    "|         |   (   )   |              |",
    "|         |    [ ]    |              |",
    "|         |   /   \\   |              |",
    "|         +-----+-----+              |",
    "|               |                    |",
    "|               |                    |",
    "\\              |                   /",
    " \\             |                  /",
    "  \\            |                 /",
    "  +------------+-----------------+",
]


def _court_pos_to_char(
    x: float, y: float, court_w: int = COURT_W, court_h: int = COURT_H
) -> Tuple[int, int]:
    """Map court position (0-47 x 0-50 feet, half-court) to char grid.

    Court coordinates: x=0-47 (baseline to halfcourt), y=0-50 (sideline to sideline).
    Char grid: col=0-33, row=0-15.
    """
    col = int(y / 50.0 * (court_w - 2)) + 1
    row = int((1.0 - x / 47.0) * (court_h - 2)) + 1
    col = max(1, min(court_w - 1, col))
    row = max(1, min(court_h - 2, row))
    return row, col


class CourtMap(Widget):
    """ASCII half-court with player positions, ball, and zones.

    Updates every tick from CourtState player positions.
    Uses Static.update() for efficient rendering.
    """

    DEFAULT_CSS = """
    CourtMap {
        height: 18;
        width: 38;
        padding: 0;
    }
    """

    # Reactive trigger for court updates
    tick_counter: reactive[int] = reactive(0)

    def __init__(
        self,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        # Offensive players: list of (x, y) positions, indexed 0-4
        self._offense: List[Tuple[float, float]] = []
        # Defensive players: list of (x, y) positions
        self._defense: List[Tuple[float, float]] = []
        # Ball carrier index (0-4 for offense, or None)
        self._ball_carrier: Optional[int] = None
        # Ball position for shots in flight
        self._ball_pos: Optional[Tuple[float, float]] = None

    def compose(self) -> ComposeResult:
        yield Static(self._render_court(), id="court-canvas")

    def _render_court(self) -> str:
        """Render the full court with players."""
        # Start with blank court
        grid = [list(line.ljust(38)) for line in _BLANK_COURT]

        # Place defensive players as 'x'
        for dx, dy in self._defense:
            row, col = _court_pos_to_char(dx, dy)
            if 0 <= row < len(grid) and 0 <= col < len(grid[row]):
                grid[row][col] = "x"

        # Place offensive players as numbers 1-5
        for i, (ox, oy) in enumerate(self._offense):
            row, col = _court_pos_to_char(ox, oy)
            if 0 <= row < len(grid) and 0 <= col < len(grid[row]):
                if self._ball_carrier == i:
                    # Ball carrier gets highlighted marker
                    if col > 0:
                        grid[row][col - 1] = "["
                    grid[row][col] = str(i + 1)
                    if col + 1 < len(grid[row]):
                        grid[row][col + 1] = "]"
                else:
                    grid[row][col] = str(i + 1)

        # Join into string
        return "\n".join("".join(row) for row in grid)

    def update_positions(
        self,
        offense: List[Tuple[float, float]] | None = None,
        defense: List[Tuple[float, float]] | None = None,
        ball_carrier: int | None = None,
        ball_pos: Tuple[float, float] | None = None,
    ) -> None:
        """Update player positions and re-render the court."""
        if offense is not None:
            self._offense = offense
        if defense is not None:
            self._defense = defense
        self._ball_carrier = ball_carrier
        self._ball_pos = ball_pos
        try:
            self.query_one("#court-canvas", Static).update(self._render_court())
        except Exception:
            pass

    def watch_tick_counter(self, _val: int) -> None:
        """Re-render on tick."""
        try:
            self.query_one("#court-canvas", Static).update(self._render_court())
        except Exception:
            pass
