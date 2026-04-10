"""New Season Setup screen -- pick seed, team count, user team.

Textual Screen with Input, Select, and Button widgets.
"""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Input, Label, Select, Static


class SeasonSetupScreen(Screen):
    """Pick season seed, number of teams, user-controlled team.

    Calls data/generator.py to create the league on confirm.
    """

    BINDINGS = [
        Binding("escape", "go_back", "Back", show=True),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        with Center():
            with Vertical(id="season-setup-form"):
                yield Static("[bold]New Season Setup[/]", markup=True)
                yield Label("Seed:")
                yield Input(value="42", id="seed-input", type="integer")
                yield Label("Number of Teams:")
                yield Select(
                    [(str(n), n) for n in [6, 10, 16, 20, 24, 30]],
                    value=30,
                    id="team-count-select",
                )
                yield Button("Generate League & Start", variant="success", id="btn-start")
                yield Button("Back", variant="error", id="btn-back")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-start":
            self._start_season()
        elif event.button.id == "btn-back":
            self.action_go_back()

    def _start_season(self) -> None:
        """Generate the league and switch to the League Hub."""
        from hoops_sim.data.generator import generate_league
        from hoops_sim.season.schedule import generate_schedule
        from hoops_sim.season.standings import Standings
        from hoops_sim.tui.screens.league_hub import LeagueHubScreen
        from hoops_sim.utils.rng import SeededRNG

        try:
            seed_val = int(self.query_one("#seed-input", Input).value)
        except (ValueError, Exception):
            seed_val = 42

        try:
            num_teams = self.query_one("#team-count-select", Select).value
            if num_teams is None or num_teams == Select.BLANK:
                num_teams = 30
        except Exception:
            num_teams = 30

        self.app.notify(f"Generating league with {num_teams} teams...")

        rng = SeededRNG(seed=seed_val)
        league = generate_league(num_teams=num_teams, rng=rng)

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
                seed=seed_val,
            )
        )

    def action_go_back(self) -> None:
        self.app.pop_screen()
