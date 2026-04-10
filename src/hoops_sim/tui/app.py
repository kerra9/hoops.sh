"""HoopsApp - curses-based App with screen routing."""

from __future__ import annotations

from hoops_sim.tui.base import App


class HoopsApp(App):
    """The hoops.sh TUI application.

    Terminal-native basketball simulation interface built with curses.
    """

    TITLE = "hoops.sh"
    SUB_TITLE = "Maximum Fidelity Basketball Simulator"
