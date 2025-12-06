from agile_ai_tui.app import AgileAIApp


def main() -> None:
    """Entry point for running the TUI via python -m agile_ai_tui."""

    app = AgileAIApp()
    app.run()


if __name__ == "__main__":
    main()
