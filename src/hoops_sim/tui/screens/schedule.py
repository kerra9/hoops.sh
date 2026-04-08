"""Schedule screen -- calendar view of SeasonSchedule."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.models.league import League
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.tui.widgets.schedule_calendar import ScheduleCalendar


class ScheduleScreen(Screen):
    """Calendar view of the season schedule.

    Highlights played/upcoming games with scores.
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(
        self,
        schedule: SeasonSchedule,
        league: League,
        current_day: int = 1,
    ) -> None:
        super().__init__()
        self.schedule = schedule
        self.league = league
        self.current_day = current_day

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="schedule-screen"):
            yield Label(f"Season Schedule -- Day {self.current_day}", classes="screen-header")
            yield Button("< Back", id="btn-back", classes="back-button")

            team_names = {t.id: t.full_name for t in self.league.teams}
            yield ScheduleCalendar(
                games=self.schedule.games,
                team_names=team_names,
                current_day=self.current_day,
                id="schedule-cal",
            )
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-back":
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
