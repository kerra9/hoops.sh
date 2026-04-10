"""League Hub screen -- central navigation during a season.

Textual Screen with standings snapshot, schedule preview, and quick actions.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Static

from hoops_sim.models.league import League
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.leader_board import LeaderBoard
from hoops_sim.tui.widgets.league_ticker import LeagueTicker
from hoops_sim.tui.widgets.mini_schedule import MiniSchedule
from hoops_sim.tui.widgets.standings_snapshot import StandingsSnapshot


class LeagueHubScreen(Screen):
    """Central navigation during a season."""

    BINDINGS = [
        Binding("t", "team_dashboard", "Team", show=True),
        Binding("s", "standings", "Standings", show=True),
        Binding("c", "schedule", "Schedule", show=True),
        Binding("a", "advance_day", "Advance Day", show=True),
        Binding("p", "play_next", "Play Next", show=True),
        Binding("escape", "main_menu", "Main Menu", show=True),
    ]

    def __init__(
        self,
        league: League,
        schedule: SeasonSchedule,
        standings: Standings,
        seed: int = 42,
        current_day: int = 1,
        user_team_id: int | None = None,
    ) -> None:
        super().__init__()
        self.league = league
        self.schedule = schedule
        self.standings = standings
        self.seed = seed
        self.current_day = current_day
        self.user_team_id = user_team_id or (
            league.teams[0].id if league.teams else 0
        )

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(id="league-hub"):
            yield Static(
                f"[bold]League Hub -- Season {self.league.season_year} -- Day {self.current_day}[/]",
                markup=True,
            )

            # Your team info
            yield Static(self._team_info(), markup=True)

            # Standings snapshots
            east_data = self._standings_data("East")
            yield StandingsSnapshot(conference="East", teams=east_data)

            west_data = self._standings_data("West")
            yield StandingsSnapshot(conference="West", teams=west_data)

            # League ticker
            results = self._recent_results()
            yield LeagueTicker(results=results)

            # Upcoming schedule
            upcoming = self._upcoming_games()
            yield MiniSchedule(games=upcoming)

            # Leaders
            yield LeaderBoard(title="TEAM LEADERS", leaders=self._team_leaders())

            # Action buttons
            with Horizontal():
                yield Button("Play Next Game", variant="success", id="btn-play")
                yield Button("Advance Day", variant="primary", id="btn-advance")
                yield Button("Team", variant="warning", id="btn-team")
                yield Button("Standings", variant="default", id="btn-standings")
                yield Button("Schedule", variant="default", id="btn-schedule")
        yield Footer()

    def _team_info(self) -> str:
        user_team = self.league.get_team(self.user_team_id)
        team_name = user_team.full_name if user_team else "Unknown"
        record = self.standings.get_record(self.user_team_id)
        record_str = record.record_display if record else "0-0"
        streak = self._get_streak(record)

        lines = [
            "[bold]YOUR TEAM[/]",
            f"  {team_name}  {record_str}",
            f"  {streak}",
        ]

        next_game = self.schedule.next_unplayed(self.user_team_id)
        if next_game:
            opp_id = (
                next_game.away_team_id
                if next_game.home_team_id == self.user_team_id
                else next_game.home_team_id
            )
            opp = self.league.get_team(opp_id)
            opp_name = opp.full_name if opp else "TBD"
            ha = "vs" if next_game.home_team_id == self.user_team_id else "@"
            lines.append(f"  Next: {ha} {opp_name} (Day {next_game.day})")
        else:
            lines.append("  Season complete")
        return "\n".join(lines)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-play":
            self.action_play_next()
        elif event.button.id == "btn-advance":
            self.action_advance_day()
        elif event.button.id == "btn-team":
            self.action_team_dashboard()
        elif event.button.id == "btn-standings":
            self.action_standings()
        elif event.button.id == "btn-schedule":
            self.action_schedule()

    def _get_streak(self, record) -> str:
        if not record:
            return ""
        if record.streak > 0:
            return f"Streak: W{record.streak}"
        if record.streak < 0:
            return f"Streak: L{abs(record.streak)}"
        return "Streak: --"

    def _standings_data(self, conference: str):
        records = self.standings.conference_standings(conference)
        if not records:
            return []
        sorted_recs = sorted(records, key=lambda r: r.win_pct, reverse=True)
        leader = sorted_recs[0] if sorted_recs else None
        result = []
        for rec in sorted_recs[:5]:
            if leader:
                gb = ((leader.wins - rec.wins) + (rec.losses - leader.losses)) / 2.0
                gb_str = "-" if gb == 0 else f"{gb:.1f}"
            else:
                gb_str = "-"
            result.append((rec.team_name[:12], rec.wins, rec.losses, gb_str))
        return result

    def _recent_results(self):
        results = []
        team_names = {t.id: t.full_name for t in self.league.teams}
        for game in reversed(self.schedule.games):
            if game.played:
                away = team_names.get(game.away_team_id, "?")
                home = team_names.get(game.home_team_id, "?")
                results.append((away, game.away_score, home, game.home_score))
                if len(results) >= 5:
                    break
        return results

    def _upcoming_games(self):
        upcoming = []
        next_game = self.schedule.next_unplayed(self.user_team_id)
        if not next_game:
            return []
        team_names = {t.id: t.full_name for t in self.league.teams}
        for game in self.schedule.games:
            if not game.played and (
                game.home_team_id == self.user_team_id
                or game.away_team_id == self.user_team_id
            ):
                is_home = game.home_team_id == self.user_team_id
                opp_id = game.away_team_id if is_home else game.home_team_id
                opp_name = team_names.get(opp_id, "?")
                ha = "vs" if is_home else "@"
                upcoming.append((game.day, ha, opp_name))
                if len(upcoming) >= 5:
                    break
        return upcoming

    def _team_leaders(self):
        return []  # Stats not tracked per-game yet

    def action_team_dashboard(self) -> None:
        from hoops_sim.tui.screens.team_dashboard import TeamDashboardScreen

        user_team = self.league.get_team(self.user_team_id)
        if user_team:
            self.app.push_screen(
                TeamDashboardScreen(team=user_team, league=self.league)
            )

    def action_standings(self) -> None:
        from hoops_sim.tui.screens.standings import StandingsScreen

        self.app.push_screen(StandingsScreen(standings=self.standings))

    def action_schedule(self) -> None:
        from hoops_sim.tui.screens.schedule import ScheduleScreen

        self.app.push_screen(
            ScheduleScreen(
                schedule=self.schedule,
                league=self.league,
                current_day=self.current_day,
                user_team_id=self.user_team_id,
            )
        )

    def action_play_next(self) -> None:
        """Play the next scheduled game for the user's team."""
        from hoops_sim.tui.screens.live_game import LiveGameScreen

        next_game = self.schedule.next_unplayed(self.user_team_id)
        if not next_game:
            self.app.notify("No more games to play!")
            return

        home_team = self.league.get_team(next_game.home_team_id)
        away_team = self.league.get_team(next_game.away_team_id)
        if home_team and away_team:
            self.app.push_screen(
                LiveGameScreen(
                    home_team=home_team,
                    away_team=away_team,
                    scheduled_game=next_game,
                    league=self.league,
                    standings=self.standings,
                    schedule=self.schedule,
                    seed=self.seed + self.current_day,
                )
            )

    def action_advance_day(self) -> None:
        """Simulate all games for the current day."""
        from hoops_sim.engine.simulator import GameSimulator
        from hoops_sim.tui.screens.sim_results import SimResultsScreen

        day_games = self.schedule.games_on_day(self.current_day)
        team_names = {t.id: t.full_name for t in self.league.teams}

        for game in day_games:
            if not game.played:
                home = self.league.get_team(game.home_team_id)
                away = self.league.get_team(game.away_team_id)
                if home and away:
                    sim = GameSimulator(
                        home_team=home,
                        away_team=away,
                        seed=self.seed + self.current_day + game.home_team_id,
                        narrate=False,
                    )
                    while not sim.is_game_over:
                        sim.step()
                    gs = sim.game_state
                    game.record_result(gs.score.home, gs.score.away)

                    same_conf = home.conference == away.conference
                    same_div = home.division == away.division
                    self.standings.record_game(
                        home.id,
                        away.id,
                        gs.score.home,
                        gs.score.away,
                        is_home_win=gs.score.home > gs.score.away,
                        is_conference=same_conf,
                        is_division=same_div,
                    )

        self.current_day += 1

        if day_games:
            self.app.push_screen(
                SimResultsScreen(
                    games=day_games,
                    team_names=team_names,
                    day=self.current_day - 1,
                    user_team_id=self.user_team_id,
                )
            )
        else:
            self.app.notify(f"No games on Day {self.current_day - 1}")

    def action_main_menu(self) -> None:
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self.app.switch_screen(MainMenuScreen())
