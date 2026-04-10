"""Schedule calendar widget -- alias for WeekCalendarGrid.

Keeps backward compatibility with imports from schedule_calendar.
"""

from __future__ import annotations

from hoops_sim.tui.widgets.week_calendar import WeekCalendarGrid

# Re-export for backward compatibility
ScheduleCalendar = WeekCalendarGrid
