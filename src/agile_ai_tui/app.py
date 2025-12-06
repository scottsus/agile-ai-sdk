from textual.app import App, ComposeResult
from textual.widgets import Footer, Header

from agile_ai_tui.screens.chat import ChatScreen


class AgileAIApp(App):
    """Main TUI application for Agile AI SDK.

    This app provides an interactive terminal interface for communicating
    with the agent team. In Phase 2, it only echoes user messages without
    agent integration.

    Example:
        >>> app = AgileAIApp()
        >>> app.run()
    """

    TITLE = "Agile AI SDK"
    CSS = """
    Screen {
        background: $surface;
    }

    Header {
        background: $primary;
    }

    Footer {
        background: $panel;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("ctrl+c", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""

        yield Header()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app is mounted - push the chat screen."""

        self.push_screen(ChatScreen())


if __name__ == "__main__":
    app = AgileAIApp()
    app.run()
