"""New Season Setup screen -- pick seed, team count, user team."""

from __future__ import annotations

from hoops_sim.tui.base import Screen, console


class SeasonSetupScreen(Screen):
    """Pick season seed, number of teams, user-controlled team.

    Calls data/generator.py to create the league on confirm.
    """

    BINDINGS = [
        ("escape", "go_back", "Back"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._seed = 42
        self._num_teams = 30

    def render(self) -> str:
        return (
            "[bold]New Season Setup[/]\n\n"
            f"  Seed: {self._seed}\n"
            f"  Number of Teams: {self._num_teams}\n"
            f"  Options: 6, 10, 16, 20, 24, 30\n\n"
            "  [bold green][G][/] Generate League & Start\n"
            "  [bold red][B][/] Back\n"
        )

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c == "g":
            self._start_season()
        elif c == "b":
            self.action_go_back()
        elif c.isdigit():
            val = int(c)
            if val in (6, 10, 16, 20, 24, 30):
                self._num_teams = val

    def _start_season(self) -> None:
        """Generate the league and switch to the League Hub."""
        from hoops_sim.data.generator import generate_league
        from hoops_sim.season.schedule import generate_schedule
        from hoops_sim.season.standings import Standings
        from hoops_sim.tui.screens.league_hub import LeagueHubScreen
        from hoops_sim.utils.rng import SeededRNG

        console.print("Generating league...")

        rng = SeededRNG(seed=self._seed)
        league = generate_league(num_teams=self._num_teams, rng=rng)

        team_ids = [t.id for t in league.teams]
        schedule = generate_schedule(team_ids, games_per_team=82, rng=rng)

        standings = Standings()
        for team in league.teams:
            standings.add_team(team.id, team.full_name, team.conference, team.division)

        self.app.switch_screen(
            LeagueHubScreen(
                league=league,
                schedule=schedule,
                standings=standings,
                seed=self._seed,
            )
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()
