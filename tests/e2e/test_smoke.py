import asyncio
from pathlib import Path

import pytest

from agile_ai_sdk import AgentTeam, EventType, TaskExecutor
from agile_ai_sdk.models.event import Event
from tests.helpers.assertions import assert_contains_event_data, assert_event_count
from tests.helpers.event_collector import EventCollector


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_agent_team_initialization() -> None:
    """Agent team initializes without crashing."""

    team = AgentTeam()

    assert team is not None
    assert hasattr(team, "start")
    assert hasattr(team, "drop_message")
    assert hasattr(team, "on")
    assert hasattr(team, "on_any_event")
    assert hasattr(team, "stop")


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_run_started_event(executor: TaskExecutor, event_collector: EventCollector) -> None:
    """RUN_STARTED event is emitted with correct task data."""

    executor.on_any_event(event_collector.collect)

    await executor.start()
    await executor.drop_message("List files")

    await event_collector.wait_for_completion()

    assert event_collector.has_event_type(EventType.RUN_STARTED)
    assert_event_count(event_collector.events, EventType.RUN_STARTED, 1)

    started_event = event_collector.get_by_type(EventType.RUN_STARTED)[0]
    assert_contains_event_data(started_event, "task", "List files")

    await executor.stop()


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_run_finished_event(executor: TaskExecutor, event_collector: EventCollector) -> None:
    """RUN_FINISHED event is emitted on completion."""

    executor.on_any_event(event_collector.collect)

    await executor.start()
    await executor.drop_message("Echo 'test'")

    await event_collector.wait_for_completion()

    assert event_collector.completed
    assert event_collector.has_event_type(EventType.RUN_FINISHED)

    finished_events = event_collector.get_by_type(EventType.RUN_FINISHED)
    assert len(finished_events) > 0

    await executor.stop()


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_event_has_required_fields(executor: TaskExecutor, event_collector: EventCollector) -> None:
    """Events have all required fields with correct types."""

    executor.on_any_event(event_collector.collect)

    await executor.start()
    await executor.drop_message("Print 'hello'")

    await event_collector.wait_for_completion()

    assert len(event_collector.events) > 0

    for event in event_collector.events:
        assert hasattr(event, "type")
        assert hasattr(event, "agent")
        assert hasattr(event, "data")
        assert isinstance(event.type, EventType)
        assert isinstance(event.data, dict)

    await executor.stop()


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_workspace_isolation(executor: TaskExecutor, workspace_dir: Path) -> None:
    """Workspace is isolated from host directory."""

    collector = EventCollector()
    executor.on_any_event(collector.collect)

    test_filename = "test_isolation_marker.txt"

    await executor.start(workspace_dir=workspace_dir)
    await executor.drop_message(f"Create a file called {test_filename} with content 'isolated'")

    await collector.wait_for_completion()

    host_file = Path.cwd() / test_filename
    assert not host_file.exists(), f"File {test_filename} should not be in host directory"

    workspace_file = workspace_dir / test_filename
    assert workspace_file.exists(), f"File {test_filename} should exist in workspace"

    await executor.stop()


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_simple_task_completion(executor: TaskExecutor, event_collector: EventCollector) -> None:
    """Agent completes a trivial task successfully."""

    executor.on_any_event(event_collector.collect)

    await executor.start()
    await executor.drop_message("Echo 'Hello, World!'")

    await event_collector.wait_for_completion()

    event_collector.assert_completed_successfully()

    assert len(event_collector.events) >= 2
    assert event_collector.events[0].type == EventType.RUN_STARTED
    assert event_collector.events[-1].type == EventType.RUN_FINISHED

    await executor.stop()


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(60)
async def test_multi_message_conversation() -> None:
    """AgentTeam supports multiple messages in one session."""

    team = AgentTeam()
    all_events: list[Event] = []
    run_finished_count = 0

    async def collect_events(event: Event):
        nonlocal run_finished_count
        all_events.append(event)
        if event.type == EventType.RUN_FINISHED:
            run_finished_count += 1

    team.on_any_event(collect_events)

    await team.start()

    # First message
    await team.drop_message("Echo 'first'")

    # Wait for first RUN_FINISHED
    timeout = 30
    start = asyncio.get_event_loop().time()
    while run_finished_count < 1:
        if asyncio.get_event_loop().time() - start > timeout:
            raise TimeoutError("Timeout waiting for first RUN_FINISHED")
        await asyncio.sleep(0.1)

    # Verify RUN_STARTED event for first message
    run_started_events = [e for e in all_events if e.type == EventType.RUN_STARTED]
    assert (
        len(run_started_events) == 1
    ), f"Expected 1 RUN_STARTED event after first message, got {len(run_started_events)}"

    # Give the agent a moment to fully complete the first run
    # (pydantic-ai may continue processing after complete_task is called)
    await asyncio.sleep(2)

    # Second message (same session)
    await team.drop_message("Echo 'second'")

    # Wait for second RUN_FINISHED
    start = asyncio.get_event_loop().time()
    while run_finished_count < 2:
        if asyncio.get_event_loop().time() - start > timeout:
            raise TimeoutError("Timeout waiting for second RUN_FINISHED")
        await asyncio.sleep(0.1)

    # Second message should NOT emit another RUN_STARTED
    run_started_events = [e for e in all_events if e.type == EventType.RUN_STARTED]
    assert len(run_started_events) == 1, f"Expected only 1 RUN_STARTED total, got {len(run_started_events)}"

    # Verify we got 2 RUN_FINISHED events
    run_finished_events = [e for e in all_events if e.type == EventType.RUN_FINISHED]
    assert len(run_finished_events) == 2, f"Expected 2 RUN_FINISHED events, got {len(run_finished_events)}"

    await team.stop()


@pytest.mark.smoke
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(30)
async def test_invalid_state_transitions(executor: TaskExecutor) -> None:
    """Invalid state transitions raise clear errors."""

    # Test 1: drop_message before start
    with pytest.raises(RuntimeError, match="must be started before sending messages"):
        await executor.drop_message("test")

    # Test 2: start twice
    await executor.start()
    with pytest.raises(RuntimeError, match="already been started"):
        await executor.start()

    # Test 3: stop is idempotent (should not raise)
    await executor.stop()
    await executor.stop()  # Second stop should be no-op
