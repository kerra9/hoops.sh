"""Sim Results screen -- summary of all games simulated in a day."""

from __future__ import annotations

from typing import Dict, List

from hoops_sim.season.schedule import ScheduledGame
from hoops_sim.tui.base import Screen
from hoops_sim.tui.theme import SCORE_GREEN, SCORE_RED


class SimResultsScreen(Screen):
    """Summary of all games simulated in a day."""

    BINDINGS = [
        ("escape", "go_back", "Back"),
        ("enter", "go_back", "Continue"),
    ]

    def __init__(
        self,
        games: List[ScheduledGame],
        team_names: Dict[int, str],
        day: int = 1,
        user_team_id: int | None = None,
    ) -> None:
        super().__init__()
        self._games = games
        self._team_names = team_names
        self._day = day
        self._user_team_id = user_team_id

    def render(self) -> str:
        lines = [f"[bold]Day {self._day} Results[/]", ""]

        for game in self._games:
            if game.played:
                away_name = self._team_names.get(
                    game.away_team_id, f"Team {game.away_team_id}"
                )
                home_name = self._team_names.get(
                    game.home_team_id, f"Team {game.home_team_id}"
                )

                if self._user_team_id:
                    if game.home_team_id == self._user_team_id:
                        color = (
                            SCORE_GREEN
                            if game.home_score > game.away_score
                            else SCORE_RED
                        )
                    elif game.away_team_id == self._user_team_id:
                        color = (
                            SCORE_GREEN
                            if game.away_score > game.home_score
                            else SCORE_RED
                        )
                    else:
                        color = "#cccccc"
                else:
                    color = "#cccccc"

                lines.append(
                    f"  [{color}]{away_name:<20} {game.away_score:>3}"
                    f"  -  "
                    f"{game.home_score:<3} {home_name}[/]"
                )

        lines.append("")
        lines.append("  [bold green][C][/] Continue")
        return "\n".join(lines)

    def handle_input(self, choice: str) -> None:
        c = choice.strip().lower()
        if c in ("c", "b", ""):
            self.action_go_back()

    def action_go_back(self) -> None:
        self.app.pop_screen()
