"""League Hub screen -- central navigation during a season."""

from __future__ import annotations

from hoops_sim.models.league import League
from hoops_sim.season.schedule import SeasonSchedule
from hoops_sim.season.standings import Standings
from hoops_sim.tui.base import Screen
from hoops_sim.tui.widgets.leader_board import LeaderBoard
from hoops_sim.tui.widgets.league_ticker import LeagueTicker
from hoops_sim.tui.widgets.mini_schedule import MiniSchedule
from hoops_sim.tui.widgets.standings_snapshot import StandingsSnapshot


class LeagueHubScreen(Screen):
    """Central navigation during a season."""

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

    def render(self) -> str:
        lines = [
            f"[bold]League Hub -- Season {self.league.season_year} -- Day {self.current_day}[/]",
            "",
        ]

        # Your team info
        lines.append("[bold]YOUR TEAM[/]")
        user_team = self.league.get_team(self.user_team_id)
        team_name = user_team.full_name if user_team else "Unknown"
        record = self.standings.get_record(self.user_team_id)
        record_str = record.record_display if record else "0-0"
        streak = self._get_streak(record)
        lines.append(f"  {team_name}  {record_str}")
        lines.append(f"  {streak}")

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

        lines.append("")

        # Standings snapshots
        east_data = self._standings_data("East")
        east_snap = StandingsSnapshot(conference="East", teams=east_data)
        lines.append(east_snap.render())
        lines.append("")
        west_data = self._standings_data("West")
        west_snap = StandingsSnapshot(conference="West", teams=west_data)
        lines.append(west_snap.render())
        lines.append("")

        # League ticker
        results = self._recent_results()
        ticker = LeagueTicker(results=results)
        lines.append(ticker.render())
        lines.append("")

        # Upcoming schedule
        upcoming = self._upcoming_games()
        sched = MiniSchedule(games=upcoming)
        lines.append(sched.render())
        lines.append("")

        # Leaders
        leaders = LeaderBoard(title="TEAM LEADERS", leaders=self._team_leaders())
        lines.append(leaders.render())
        lines.append("")

        # Hotkey bar
        lines.append(
            "  [bold green][T][/]eam  "
            "[bold blue][S][/]tandings  "
            "[bold yellow][C][/]alendar  "
            "[bold green][A][/]dvance Day  "
            "[bold red][M][/] Main Menu"
        )
        return "\n".join(lines)

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "t":
            self.action_team_dashboard()
        elif c == "s":
            self.action_standings()
        elif c == "c":
            self.action_schedule()
        elif c == "a":
            self.action_advance_day()
        elif c == "m":
            self.action_main_menu()

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
                    ha = "vs" if game.home_team_id == self.user_team_id else "@"
                    upcoming.append((day, ha, opp_name))
            if len(upcoming) >= 5:
                break
        return upcoming[:5]

    def _team_leaders(self):
        return [
            ("PPG", "Top Scorer", "25.0"),
            ("RPG", "Top Rebounder", "10.0"),
            ("APG", "Top Passer", "8.0"),
        ]

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

    def _quick_sim_game(self, game) -> None:
        """Quick sim a non-user game."""
        from hoops_sim.engine.simulator import GameSimulator

        home = self.league.get_team(game.home_team_id)
        away = self.league.get_team(game.away_team_id)
        if not home or not away:
            return

        sim = GameSimulator(home_team=home, away_team=away, seed=self.seed + game.game_id)
        while not sim.is_game_over:
            sim.step()

        gs = sim.game_state
        game.record_result(gs.score.home, gs.score.away)

        same_conf = home.conference == away.conference
        same_div = home.division == away.division
        self.standings.record_game(
            home.id, away.id, gs.score.home, gs.score.away,
            is_home_win=gs.score.home > gs.score.away,
            is_conference=same_conf, is_division=same_div,
        )

    def action_main_menu(self) -> None:
        from hoops_sim.tui.screens.main_menu import MainMenuScreen

        self.app.switch_screen(MainMenuScreen())
