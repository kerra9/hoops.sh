"""Shooting chart -- alias for CourtShootingChart.

Keeps backward compatibility with imports.
"""

from __future__ import annotations

from hoops_sim.tui.widgets.court_shooting_chart import CourtShootingChart

# Re-export
ShootingChart = CourtShootingChart
