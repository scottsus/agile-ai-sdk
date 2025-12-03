from pathlib import Path

import pytest

from agile_ai_sdk import AgentTeam
from tests.helpers.assertions import assert_no_errors
from tests.helpers.event_collector import EventCollector
from tests.helpers.llm_judge import LLMJudge
from tests.helpers.workspace_utils import (
    assert_file_exists,
    assert_tests_pass,
    get_workspace_dir,
)


@pytest.mark.scenario
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(900)
async def test_add_health_endpoint(agent_team: AgentTeam, event_collector: EventCollector, base_dir: Path) -> None:
    """Add /health endpoint to FastAPI app with tests."""

    task = (
        "Add a /health endpoint to the FastAPI app in main.py that returns "
        "{'status': 'healthy', 'version': '1.0.0'}. "
        "Also add a test_health() function in test_main.py that verifies "
        "the endpoint returns status code 200 and the correct JSON response. "
        "Make sure all tests pass by running pytest."
    )

    await event_collector.collect_until_done(agent_team.execute(task))
    event_collector.assert_completed_successfully()

    run_id = event_collector.get_run_id()
    assert run_id is not None, "No run_id found in events"

    workspace_dir = get_workspace_dir(base_dir, run_id)

    assert_file_exists(workspace_dir, "main.py")
    assert_file_exists(workspace_dir, "test_main.py")

    judge = LLMJudge()
    evaluation = await judge.evaluate_task_completion(
        task=task,
        events=event_collector.events,
        workspace_dir=workspace_dir,
    )

    assert evaluation.task_completed, (
        f"Task not completed according to LLM judge.\n"
        f"Confidence: {evaluation.confidence}\n"
        f"Reasoning: {evaluation.reasoning}\n"
        f"Issues: {evaluation.issues_found}"
    )

    assert_tests_pass(workspace_dir, "pytest -v")

    assert_no_errors(event_collector.events)


@pytest.mark.scenario
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(900)
async def test_fix_broken_code(agent_team: AgentTeam, event_collector: EventCollector, base_dir: Path) -> None:
    """Fix all bugs in broken_code fixture."""

    task = (
        "Run pytest on test_buggy.py to see which tests are failing. "
        "You will find that calculate_average() and find_max() in buggy.py "
        "don't handle empty lists correctly. Fix both functions to raise "
        "ValueError when given an empty list. The error messages should be: "
        "'Cannot calculate average of empty list' for calculate_average and "
        "'Cannot find maximum of empty list' for find_max. "
        "After fixing, run the tests again to make sure all tests pass."
    )

    await event_collector.collect_until_done(agent_team.execute(task))

    event_collector.assert_completed_successfully()

    run_id = event_collector.get_run_id()
    assert run_id is not None, "No run_id found in events"

    workspace_dir = get_workspace_dir(base_dir, run_id)

    assert_file_exists(workspace_dir, "buggy.py")
    assert_file_exists(workspace_dir, "test_buggy.py")

    judge = LLMJudge()
    evaluation = await judge.evaluate_task_completion(
        task=task,
        events=event_collector.events,
        workspace_dir=workspace_dir,
    )

    assert evaluation.task_completed, (
        f"Task not completed according to LLM judge.\n"
        f"Confidence: {evaluation.confidence}\n"
        f"Reasoning: {evaluation.reasoning}\n"
        f"Issues: {evaluation.issues_found}"
    )

    assert_tests_pass(workspace_dir, "pytest -v")

    assert_no_errors(event_collector.events)


@pytest.mark.scenario
@pytest.mark.e2e
@pytest.mark.asyncio
@pytest.mark.timeout(900)
async def test_add_feature_with_tests(agent_team: AgentTeam, event_collector: EventCollector, base_dir: Path) -> None:
    """Add complete feature with implementation, tests, and documentation."""

    task = (
        "Add a divide(a, b) function to calculator.py that returns a / b. "
        "The function should raise ValueError with message 'Cannot divide by zero' "
        "when b is 0. Add a comprehensive docstring following Google style. "
        "In test_calculator.py, add test_divide() and test_divide_by_zero() functions. "
        "test_divide() should test normal division cases (e.g., 10/2=5, 15/3=5). "
        "test_divide_by_zero() should verify that dividing by zero raises ValueError. "
        "Run pytest to make sure all tests pass."
    )

    await event_collector.collect_until_done(agent_team.execute(task))

    event_collector.assert_completed_successfully()

    run_id = event_collector.get_run_id()
    assert run_id is not None, "No run_id found in events"

    workspace_dir = get_workspace_dir(base_dir, run_id)

    assert_file_exists(workspace_dir, "calculator.py")
    assert_file_exists(workspace_dir, "test_calculator.py")

    judge = LLMJudge()
    evaluation = await judge.evaluate_task_completion(
        task=task,
        events=event_collector.events,
        workspace_dir=workspace_dir,
    )

    assert evaluation.task_completed, (
        f"Task not completed according to LLM judge.\n"
        f"Confidence: {evaluation.confidence}\n"
        f"Reasoning: {evaluation.reasoning}\n"
        f"Issues: {evaluation.issues_found}"
    )

    assert_tests_pass(workspace_dir, "pytest -v")

    assert_no_errors(event_collector.events)
