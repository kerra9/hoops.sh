"""Schedule screen -- week calendar grid view of SeasonSchedule."""

from __future__ import annotations

from typing import Optional, Tuple

from hoops_sim.models.league import League
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.tui.base import Screen
from hoops_sim.tui.widgets.season_progress import SeasonProgressBar
from hoops_sim.tui.widgets.week_calendar import WeekCalendarGrid


class ScheduleScreen(Screen):
    """Calendar view of the season schedule with week navigation."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("left_square_bracket", "prev_week", "Prev Week"),
        ("right_square_bracket", "next_week", "Next Week"),
    ]

    def __init__(
        self,
        schedule: SeasonSchedule,
        league: League,
        current_day: int = 1,
        user_team_id: int | None = None,
    ) -> None:
        super().__init__()
        self.schedule = schedule
        self.league = league
        self.current_day = current_day
        self.user_team_id = user_team_id or (
            league.teams[0].id if league.teams else 0
        )
        self._week_start = max(1, current_day - (current_day - 1) % 7)

    def render(self) -> str:
        lines = [
            f"[bold]Season Schedule -- Day {self.current_day}[/]",
            "  [bold][[/] Prev Week    [bold]][/] Next Week    [bold red][B][/] Back",
            "",
        ]

        day_games = self._build_week_games()
        wc = WeekCalendarGrid(
            week_start=self._week_start,
            current_day=self.current_day,
            day_games=day_games,
        )
        lines.append(wc.render())
        lines.append("")

        games_played = sum(
            1
            for g in self.schedule.games
            if g.played
            and (
                g.home_team_id == self.user_team_id
                or g.away_team_id == self.user_team_id
            )
        )
        sp = SeasonProgressBar(games_played=games_played, total_games=82)
        lines.append(sp.render())
        return "\n".join(lines)

    def _build_week_games(self):
        day_games = {}
        team_names = {t.id: t.full_name for t in self.league.teams}

        for day_offset in range(7):
            day = self._week_start + day_offset
            games = self.schedule.games_on_day(day)
            for game in games:
                if (
                    game.home_team_id == self.user_team_id
                    or game.away_team_id == self.user_team_id
                ):
                    is_home = game.home_team_id == self.user_team_id
                    opp_id = game.away_team_id if is_home else game.home_team_id
                    opp_name = team_names.get(opp_id, f"Team {opp_id}")
                    ha = "vs" if is_home else "@"

                    if game.played:
                        day_games[day] = (
                            ha, opp_name, game.home_score, game.away_score, is_home,
                        )
                    else:
                        day_games[day] = (ha, opp_name, None, None, is_home)
        return day_games

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "[":
            self.action_prev_week()
        elif c == "]":
            self.action_next_week()
        elif c == "b":
            self.action_go_back()

    def action_prev_week(self) -> None:
        self._week_start = max(1, self._week_start - 7)

    def action_next_week(self) -> None:
        self._week_start += 7

    def action_go_back(self) -> None:
        self.app.pop_screen()
