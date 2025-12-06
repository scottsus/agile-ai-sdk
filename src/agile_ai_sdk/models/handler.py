from collections.abc import Awaitable, Callable

from agile_ai_sdk.models.event import Event

SyncEventHandler = Callable[[Event], None]
AsyncEventHandler = Callable[[Event], Awaitable[None]]
EventHandler = SyncEventHandler | AsyncEventHandler
