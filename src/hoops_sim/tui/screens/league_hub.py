"""League Hub screen -- central navigation during a season.

Redesigned as a 3x2 dashboard with team info, ticker, standings,
schedule, and stat leaders.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label

from hoops_sim.models.league import League
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.widgets.leader_board import LeaderBoard
from hoops_sim.tui.widgets.league_ticker import LeagueTicker
from hoops_sim.tui.widgets.mini_schedule import MiniSchedule
from hoops_sim.tui.widgets.standings_snapshot import StandingsSnapshot


class LeagueHubScreen(Screen):
    """Central navigation during a season.

    3x2 dashboard layout with:
    - Your team info + league ticker
    - Standings snapshot + upcoming schedule
    - Team leaders + league leaders
    - Footer hotkey bar
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
        self.user_team_id = user_team_id or (
            league.teams[0].id if league.teams else 0
        )

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="league-hub"):
            yield Label(
                f"[bold]League Hub -- Season {self.league.season_year} -- Day {self.current_day}[/]",
                id="league-hub-header",
            )

            with Horizontal(id="league-hub-grid"):
                # Left column
                with Vertical():
                    # Your team info
                    yield Label("[bold]YOUR TEAM[/]")
                    user_team = self.league.get_team(self.user_team_id)
                    team_name = user_team.full_name if user_team else "Unknown"
                    record = self.standings.get_record(self.user_team_id)
                    record_str = record.record_display if record else "0-0"
                    streak = self._get_streak(record)

                    yield Label(f"  {team_name}  {record_str}")
                    yield Label(f"  {streak}")

                    next_game = self.schedule.next_unplayed(self.user_team_id)
                    if next_game:
                        opp_id = (
                            next_game.away_team_id
                            if next_game.home_team_id == self.user_team_id
                            else next_game.home_team_id
                        )
                        opp = self.league.get_team(opp_id)
                        opp_name = opp.full_name if opp else "TBD"
                        ha = (
                            "vs"
                            if next_game.home_team_id == self.user_team_id
                            else "@"
                        )
                        yield Label(f"  Next: {ha} {opp_name} (Day {next_game.day})")
                    else:
                        yield Label("  Season complete")

                    yield Label("")

                    # Standings snapshot
                    east_data = self._standings_data("East")
                    yield StandingsSnapshot(
                        conference="East",
                        teams=east_data,
                        id="east-snapshot",
                    )
                    yield Label("")
                    west_data = self._standings_data("West")
                    yield StandingsSnapshot(
                        conference="West",
                        teams=west_data,
                        id="west-snapshot",
                    )

                # Right column
                with Vertical():
                    # League ticker
                    results = self._recent_results()
                    yield LeagueTicker(results=results, id="hub-ticker")
                    yield Label("")

                    # Upcoming schedule
                    upcoming = self._upcoming_games()
                    yield MiniSchedule(games=upcoming, id="hub-schedule")
                    yield Label("")

                    # Team leaders
                    yield LeaderBoard(
                        title="TEAM LEADERS",
                        leaders=self._team_leaders(),
                        id="hub-team-leaders",
                    )

            # Hotkey bar
            yield Label(
                "  [bold green][T][/]eam  "
                "[bold blue][S][/]tandings  "
                "[bold yellow][C][/]alendar  "
                "[bold green][A][/]dvance Day  "
                "[bold red][Esc][/] Main Menu",
                classes="hotkey-bar",
            )
        yield Footer()

    def _get_streak(self, record) -> str:
        """Format streak display."""
        if not record:
            return ""
        if record.streak > 0:
            return f"Streak: W{record.streak}"
        if record.streak < 0:
            return f"Streak: L{abs(record.streak)}"
        return "Streak: --"

    def _standings_data(self, conference: str):
        """Get top 5 standings for a conference."""
        records = self.standings.conference_standings(conference)
        if not records:
            return []
        sorted_recs = sorted(records, key=lambda r: r.win_pct, reverse=True)
        leader = sorted_recs[0] if sorted_recs else None
        result = []
        for rec in sorted_recs[:5]:
            if leader:
                gb = (
                    (leader.wins - rec.wins) + (rec.losses - leader.losses)
                ) / 2.0
                gb_str = "-" if gb == 0 else f"{gb:.1f}"
            else:
                gb_str = "-"
            result.append((rec.team_name[:12], rec.wins, rec.losses, gb_str))
        return result

    def _recent_results(self):
        """Get recent game results as formatted strings."""
        results = []
        for day in range(max(1, self.current_day - 3), self.current_day):
            games = self.schedule.games_on_day(day)
            for game in games:
                if game.played:
                    home = self.league.get_team(game.home_team_id)
                    away = self.league.get_team(game.away_team_id)
                    h_name = home.abbreviation if home else "???"
                    a_name = away.abbreviation if away else "???"
                    results.append(
                        f"{a_name} {game.away_score} - {h_name} {game.home_score}"
                    )
        return results[-5:]

    def _upcoming_games(self):
        """Get upcoming games for the user's team."""
        upcoming = []
        for day in range(self.current_day, self.current_day + 20):
            games = self.schedule.games_on_day(day)
            for game in games:
                if not game.played and (
                    game.home_team_id == self.user_team_id
                    or game.away_team_id == self.user_team_id
                ):
                    opp_id = (
                        game.away_team_id
                        if game.home_team_id == self.user_team_id
                        else game.home_team_id
                    )
                    opp = self.league.get_team(opp_id)
                    opp_name = opp.full_name if opp else "TBD"
                    ha = (
                        "vs"
                        if game.home_team_id == self.user_team_id
                        else "@"
                    )
                    upcoming.append((day, ha, opp_name))
            if len(upcoming) >= 5:
                break
        return upcoming[:5]

    def _team_leaders(self):
        """Get placeholder team leader stats."""
        # Real implementation would pull from season stats
        return [
            ("PPG", "Top Scorer", "25.0"),
            ("RPG", "Top Rebounder", "10.0"),
            ("APG", "Top Passer", "8.0"),
        ]

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
                    game.home_team_id,
                    game.away_team_id,
                    home_score,
                    away_score,
                    is_home_win=True,
                    is_conference=same_conf,
                    is_division=same_div,
                )
            else:
                self.standings.record_game(
                    game.home_team_id,
                    game.away_team_id,
                    home_score,
                    away_score,
                    is_home_win=False,
                    is_conference=same_conf,
                    is_division=same_div,
                )

    def action_main_menu(self) -> None:
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self.app.switch_screen(MainMenuScreen())
