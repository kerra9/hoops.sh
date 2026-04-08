"""Visual salary cap / luxury tax / apron thresholds."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import Label

from hoops_sim.models.league import SalaryCapInfo


def _format_money(amount: int) -> str:
    """Format salary as $XXM."""
    return f"${amount / 1_000_000:.1f}M"


class SalaryCapBar(Widget):
    """Visual salary cap bar showing payroll vs cap thresholds.

    Displays the team's payroll relative to salary cap, luxury tax,
    and apron thresholds.
    """

    DEFAULT_CSS = """
    SalaryCapBar {
        height: 5;
        width: 100%;
        padding: 0 1;
    }
    """

    def __init__(
        self,
        payroll: int = 0,
        cap_info: SalaryCapInfo | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._payroll = payroll
        self._cap = cap_info or SalaryCapInfo()

    def compose(self) -> ComposeResult:
        cap = self._cap
        payroll = self._payroll

        # Determine color based on payroll position
        if payroll > cap.second_apron:
            color = "#e74c3c"
            status = "ABOVE 2ND APRON"
        elif payroll > cap.first_apron:
            color = "#e67e22"
            status = "Above 1st Apron"
        elif payroll > cap.luxury_tax_threshold:
            color = "#f1c40f"
            status = "Luxury Tax"
        elif payroll > cap.salary_cap:
            color = "#3498db"
            status = "Over Cap"
        else:
            color = "#2ecc71"
            status = "Under Cap"

        # Build a visual bar
        max_val = cap.second_apron + 20_000_000
        bar_len = 30
        fill_len = min(bar_len, int(payroll / max_val * bar_len))
        filled = "\u2588" * fill_len
        empty = "\u2591" * (bar_len - fill_len)
        bar = f"[{color}]{filled}[/]{empty}"

        with Vertical(classes="salary-cap-bar"):
            yield Label(f"Payroll: {_format_money(payroll)}  [{color}]{status}[/]")
            yield Label(bar)
            yield Label(
                f"Cap: {_format_money(cap.salary_cap)}  "
                f"Tax: {_format_money(cap.luxury_tax_threshold)}  "
                f"Apron: {_format_money(cap.first_apron)}"
            )
