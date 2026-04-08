"""New Season Setup screen -- pick seed, team count, user team."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Label, Select

from hoops_sim.tui.widgets.seed_input import SeedInput


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

    def compose(self) -> ComposeResult:
        yield Header()
        with Center(id="season-setup"):
            with Vertical(id="season-setup-form"):
                yield Label("New Season Setup", id="setup-title")
                yield Label("")
                yield SeedInput(initial_seed=42, id="season-seed")
                yield Label("")
                yield Label("Number of Teams:")
                yield Select(
                    [(str(n), n) for n in [6, 10, 16, 20, 24, 30]],
                    value=30,
                    id="team-count",
                )
                yield Label("")
                yield Button("Generate League & Start", id="btn-start-season", variant="primary")
                yield Button("Back", id="btn-back", variant="default")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start-season":
            self._start_season()
        elif event.button.id == "btn-back":
            self.action_go_back()

    def on_seed_input_seed_changed(self, event: SeedInput.SeedChanged) -> None:
        self._seed = event.seed

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "team-count" and event.value is not None:
            self._num_teams = int(event.value)

    def _start_season(self) -> None:
        """Generate the league and switch to the League Hub."""
        from hoops_sim.data.generator import generate_league
        from hoops_sim.season.schedule import generate_schedule
        from hoops_sim.season.standings import Standings
        from hoops_sim.tui.screens.league_hub import LeagueHubScreen
        from hoops_sim.utils.rng import SeededRNG

        self.notify("Generating league...", title="Please wait")

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
