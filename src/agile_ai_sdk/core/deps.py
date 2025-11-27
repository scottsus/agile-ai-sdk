from dataclasses import dataclass

from agile_ai_sdk.core.events import EventStream
from agile_ai_sdk.core.router import MessageRouter


@dataclass
class AgentDeps:
    """Dependencies shared across all agents.

    Attributes:
        router: Message router for inter-agent communication
        event_stream: Event stream for observability
    """

    router: MessageRouter
    event_stream: EventStream
