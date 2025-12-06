from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.screen import Screen
from textual.widgets import Input, Static


class ChatMessage(Static):
    """Widget representing a single chat message.

    In Phase 2, all messages are user messages. In Phase 3, we'll add
    agent messages with different styling.
    """

    def __init__(self, content: str, sender: str = "You") -> None:

        super().__init__()
        self.content = content
        self.sender = sender
        self.update(f"[bold]{self.sender}:[/bold] {self.content}")


class ChatScreen(Screen):
    """Main chat interface screen.

    This screen displays a scrollable message history and an input field
    for user messages. In Phase 2, messages are simply echoed back.
    Phase 3 will integrate with the agent team.

    User workflow:
    1. Type message in input field
    2. Press Enter to submit
    3. Message appears as "You: [message]"
    4. Input field clears and refocuses
    5. Press 'q' to quit

    Example:
        User types "Hello" and presses Enter
        -> Message appears as "You: Hello"
        -> Input clears, ready for next message
    """

    CSS = """
    ChatScreen {
        layout: vertical;
    }

    #message-container {
        height: 1fr;
        border: solid $primary;
        padding: 1;
        background: $surface;
    }

    ChatMessage {
        margin-bottom: 1;
    }

    Input {
        dock: bottom;
        height: 3;
        border: solid $accent;
    }
    """

    def compose(self) -> ComposeResult:
        """Create child widgets for the chat screen."""

        yield VerticalScroll(id="message-container")
        yield Input(placeholder="Type a message...", id="user-input")

    def on_mount(self) -> None:
        """Called when screen is mounted - focus the input field."""

        self.query_one("#user-input", Input).focus()

    @on(Input.Submitted)
    async def handle_message_submit(self, event: Input.Submitted) -> None:
        """Handle user message submission.

        This function:
        1. extracts and validates the message text
        2. clears the input field
        3. creates a ChatMessage widget
        4. adds it to the message container
        5. auto-scrolls to show the new message

        In Phase 2: Simply echo the message back to the chat
        In Phase 3: Will send to agent team and stream responses
        """

        message = event.value.strip()

        if not message:
            return

        event.input.value = ""

        container = self.query_one("#message-container", VerticalScroll)
        await container.mount(ChatMessage(message, sender="You"))

        container.scroll_end(animate=False)
