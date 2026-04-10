"""CLI entry point for hoops-sim."""

from __future__ import annotations


def main() -> None:
    """Main entry point -- launches the Rich-only TUI."""
    from hoops_sim.tui.app import HoopsApp

    app = HoopsApp()
    app.run()


if __name__ == "__main__":
    main()
