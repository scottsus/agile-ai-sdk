import asyncio
from typing import TYPE_CHECKING, Any

from agile_ai_sdk.models import Event, EventType

if TYPE_CHECKING:
    from tests.logging.run_logger import TestRunLogger


class EventCollector:
    """Helper to collect and analyze events using handlers.

    This class:
    1. collects events via handler registration
    2. provides assertion helpers for event validation
    3. extracts metadata like run_id and final results
    4. optionally logs events to a test run logger
    5. waits for completion with configurable timeout

    Example:
        >>> collector = EventCollector(test_run_logger=logger)
        >>> executor.on_any_event(collector.collect)
        >>> await collector.wait_for_completion()
        >>> collector.assert_completed_successfully()
    """

    def __init__(self, test_run_logger: "TestRunLogger | None" = None) -> None:
        """Initialize event collector.

        Args:
            test_run_logger: Optional TestRunLogger to log events
        """

        self.events: list[Event] = []
        self.completed: bool = False
        self.error: str | None = None
        self.test_run_logger: TestRunLogger | None = test_run_logger
        self._completion_event: asyncio.Event = asyncio.Event()

    async def collect(self, event: Event) -> None:
        """Handler to collect events."""

        self.events.append(event)

        if self.test_run_logger:
            self.test_run_logger.log_event(event)

        if event.type == EventType.RUN_FINISHED:
            self.completed = True
            self._completion_event.set()

        elif event.type == EventType.RUN_ERROR:
            self.completed = True
            self.error = event.data.get("error", "Unknown error")
            self._completion_event.set()

    async def wait_for_completion(self, timeout: float = 300) -> None:
        """Wait for RUN_FINISHED or RUN_ERROR event."""

        await asyncio.wait_for(self._completion_event.wait(), timeout=timeout)

    def get_by_type(self, event_type: EventType) -> list[Event]:
        """Get all events of specific type."""

        return [e for e in self.events if e.type == event_type]

    def has_event_type(self, event_type: EventType) -> bool:
        """Check if event type occurred."""

        return any(e.type == event_type for e in self.events)

    def get_event_types(self) -> list[EventType]:
        """Get list of all event types in order."""

        return [e.type for e in self.events]

    def assert_completed_successfully(self) -> None:
        """Assert that execution completed without error."""

        assert self.completed, "Execution did not complete"
        assert self.error is None, f"Execution failed with error: {self.error}"

    def assert_has_events(self, expected_types: list[EventType]) -> None:
        """Assert that all expected event types occurred (order doesn't matter)."""

        actual_types = set(self.get_event_types())
        expected_set = set(expected_types)
        missing = expected_set - actual_types
        assert not missing, f"Missing expected event types: {missing}"

    def assert_event_sequence(self, expected_types: list[EventType]) -> None:
        """Assert that events occurred in specific order (allows extra events between).

        Example:
            >>> collector.assert_event_sequence([
            ...     EventType.RUN_STARTED,
            ...     EventType.STEP_STARTED,
            ...     EventType.RUN_FINISHED
            ... ])
        """

        actual_types = self.get_event_types()
        expected_idx = 0

        for actual_type in actual_types:
            if expected_idx < len(expected_types) and actual_type == expected_types[expected_idx]:
                expected_idx += 1

        assert expected_idx == len(expected_types), (
            f"Event sequence mismatch. Expected {expected_types}, "
            f"but got {actual_types}. Matched {expected_idx}/{len(expected_types)}"
        )

    def get_run_id(self) -> str | None:
        """Extract run_id from RUN_STARTED event."""

        started_events = self.get_by_type(EventType.RUN_STARTED)
        if not started_events:
            return None
        return started_events[0].data.get("run_id")

    def get_final_result(self) -> dict[str, Any]:
        """Get final result data from RUN_FINISHED event."""

        finished_events = self.get_by_type(EventType.RUN_FINISHED)
        if not finished_events:
            return {}
        return finished_events[-1].data

    def print_summary(self) -> None:
        """Print summary of collected events (useful for debugging)."""

        print(f"\nCollected {len(self.events)} events:")
        for i, event in enumerate(self.events):
            print(f"  {i+1}. [{event.agent.value}] {event.type.value}")
            if event.data:
                print(f"     Data: {event.data}")
        print(f"Completed: {self.completed}")
        if self.error:
            print(f"Error: {self.error}")
