"""League Hub screen -- central navigation during a season."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.models.league import League
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings


class LeagueHubScreen(Screen):
    """Central navigation during a season.

    Shows current day, next game, record, quick links.
    """

    BINDINGS = [
        ("t", "team_dashboard", "Team"),
        ("s", "standings", "Standings"),
        ("c", "schedule", "Schedule"),
        ("a", "advance_day", "Advance Day"),
        ("escape", "main_menu", "Main Menu"),
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
        # Default to first team if no user team specified
        self.user_team_id = user_team_id or (league.teams[0].id if league.teams else 0)

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="league-hub"):
            yield Label(
                f"Season {self.league.season_year} -- Day {self.current_day}",
                id="league-hub-header",
            )
            with Vertical(id="league-hub-info"):
                user_team = self.league.get_team(self.user_team_id)
                team_name = user_team.full_name if user_team else "Unknown"
                record = self.standings.get_record(self.user_team_id)
                record_str = record.record_display if record else "0-0"
                next_game = self.schedule.next_unplayed(self.user_team_id)
                if next_game:
                    opp_id = (
                        next_game.away_team_id
                        if next_game.home_team_id == self.user_team_id
                        else next_game.home_team_id
                    )
                    opp = self.league.get_team(opp_id)
                    opp_name = opp.full_name if opp else "TBD"
                    home_away = "vs" if next_game.home_team_id == self.user_team_id else "@"
                    next_str = f"Day {next_game.day}: {home_away} {opp_name}"
                else:
                    next_str = "Season complete"

                yield Label(f"Your Team: {team_name}  ({record_str})")
                yield Label(f"Next Game: {next_str}")
                yield Label(f"Seed: {self.seed}")

            with Horizontal(id="league-hub-nav"):
                yield Button("Team Dashboard", id="btn-team", variant="primary")
                yield Button("Standings", id="btn-standings", variant="default")
                yield Button("Schedule", id="btn-schedule", variant="default")
                yield Button("Advance Day", id="btn-advance", variant="success")
                yield Button("Main Menu", id="btn-main-menu", variant="error")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-team":
            self.action_team_dashboard()
        elif event.button.id == "btn-standings":
            self.action_standings()
        elif event.button.id == "btn-schedule":
            self.action_schedule()
        elif event.button.id == "btn-advance":
            self.action_advance_day()
        elif event.button.id == "btn-main-menu":
            self.action_main_menu()

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
            )
        )

    def action_advance_day(self) -> None:
        """Advance to the next day, simulating any games."""
        games_today = self.schedule.games_on_day(self.current_day)
        user_game = None

        for game in games_today:
            if game.played:
                continue
            if (
                game.home_team_id == self.user_team_id
                or game.away_team_id == self.user_team_id
            ):
                user_game = game
            else:
                # Auto-sim non-user games with simple random scores
                self._quick_sim_game(game)

        if user_game and not user_game.played:
            from hoops_sim.tui.screens.live_game import LiveGameScreen

            home = self.league.get_team(user_game.home_team_id)
            away = self.league.get_team(user_game.away_team_id)
            if home and away:
                self.app.push_screen(
                    LiveGameScreen(
                        home_team=home,
                        away_team=away,
                        scheduled_game=user_game,
                        league=self.league,
                        standings=self.standings,
                        schedule=self.schedule,
                        seed=self.seed,
                    )
                )
                return

        self.current_day += 1
        # Refresh the screen
        self.app.switch_screen(
            LeagueHubScreen(
                league=self.league,
                schedule=self.schedule,
                standings=self.standings,
                seed=self.seed,
                current_day=self.current_day,
                user_team_id=self.user_team_id,
            )
        )

    def _quick_sim_game(self, game: "ScheduledGame") -> None:
        """Quick-sim a game using the real GameSimulator at max speed."""
        from hoops_sim.engine.simulator import GameSimulator

        home_team = self.league.get_team(game.home_team_id)
        away_team = self.league.get_team(game.away_team_id)
        if not home_team or not away_team:
            return

        sim = GameSimulator(
            home_team=home_team,
            away_team=away_team,
            seed=self.seed + game.game_id,
            narrate=False,
        )
        result = sim.simulate_full_game()
        home_score = result.home_score
        away_score = result.away_score
        # Avoid ties (overtime should handle this, but just in case)
        if home_score == away_score:
            home_score += 1
        game.record_result(home_score, away_score)

        home_team = self.league.get_team(game.home_team_id)
        away_team = self.league.get_team(game.away_team_id)
        if home_team and away_team:
            same_conf = home_team.conference == away_team.conference
            same_div = home_team.division == away_team.division
            if home_score > away_score:
                self.standings.record_game(
                    game.home_team_id, game.away_team_id,
                    home_score, away_score,
                    is_home_win=True, is_conference=same_conf, is_division=same_div,
                )
            else:
                self.standings.record_game(
                    game.home_team_id, game.away_team_id,
                    home_score, away_score,
                    is_home_win=False, is_conference=same_conf, is_division=same_div,
                )

    def action_main_menu(self) -> None:
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self.app.switch_screen(MainMenuScreen())
