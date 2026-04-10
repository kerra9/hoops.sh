"""Generic scoreboard widget -- alias for BroadcastScoreboard.

Keeps backward compatibility with imports.
"""

from __future__ import annotations

from hoops_sim.tui.widgets.broadcast_scoreboard import BroadcastScoreboard

# Re-export
Scoreboard = BroadcastScoreboard
