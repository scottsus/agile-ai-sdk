import re
import subprocess
from pathlib import Path

"""Workspace filesystem utilities for validating what actually happened.

This module contains utilities that validate the workspace filesystem - what
ACTUALLY HAPPENED on disk. For assertions that validate what the agent REPORTED
doing via events, see assertions.py.

Example:
    assert_file_contains(workspace, "foo.py", "bar")  # Does foo.py actually contain "bar"?
    vs.
    assert_file_modified(events, "foo.py")  # Did agent report modifying foo.py?
"""


def get_workspace_dir(base_dir: Path, run_id: str) -> Path:
    """Gets workspace directory for a run.

    This function:
    1. constructs the path from base_dir and run_id
    2. returns the workspace subdirectory path

    Args:
        base_dir: Base directory for runs (usually tmp_path / "runs")
        run_id: Run ID from RUN_STARTED event

    Returns:
        Path to workspace directory

    Example:
        >>> workspace = get_workspace_dir(tmp_path / "runs", "abc123")
        >>> assert workspace == tmp_path / "runs" / "abc123" / "workspace"
    """
    return base_dir / run_id / "workspace"


def assert_file_exists(workspace_dir: Path, relative_path: str) -> None:
    """Asserts that file exists in workspace."""

    file_path = workspace_dir / relative_path
    assert file_path.exists(), f"File not found: {relative_path}"


def assert_file_contains(workspace_dir: Path, relative_path: str, content: str) -> None:
    """Asserts that file contains specific content."""

    file_path = workspace_dir / relative_path
    assert file_path.exists(), f"File not found: {relative_path}"
    actual_content = file_path.read_text()
    assert content in actual_content, (
        f"Content not found in {relative_path}.\n"
        f"Looking for: {content}\n"
        f"File contains: {actual_content[:200]}..."
    )


def assert_file_matches_regex(workspace_dir: Path, relative_path: str, pattern: str) -> None:
    """Asserts that file content matches regex pattern."""

    file_path = workspace_dir / relative_path
    assert file_path.exists(), f"File not found: {relative_path}"
    actual_content = file_path.read_text()
    assert re.search(pattern, actual_content), (
        f"Pattern not found in {relative_path}.\n" f"Pattern: {pattern}\n" f"File contains: {actual_content[:200]}..."
    )


def read_file(workspace_dir: Path, relative_path: str) -> str:
    """Reads file content from workspace."""

    file_path = workspace_dir / relative_path
    assert file_path.exists(), f"File not found: {relative_path}"
    return file_path.read_text()


def assert_tests_pass(workspace_dir: Path, test_command: str = "pytest") -> None:
    """Runs tests in workspace and asserts they pass.

    This function:
    1. executes the test command in the workspace directory
    2. captures stdout and stderr
    3. asserts that the return code is 0 (success)

    Example:
        >>> assert_tests_pass(workspace_dir)
        >>> assert_tests_pass(workspace_dir, "pytest -v")
    """
    command_parts = test_command.split()
    result = subprocess.run(
        command_parts,
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, (
        f"Tests failed in workspace.\n" f"stdout: {result.stdout}\n" f"stderr: {result.stderr}"
    )


def run_command_in_workspace(workspace_dir: Path, command: str) -> tuple[int, str, str]:
    """Executes command in workspace and returns result.

    This function:
    1. runs the command in the workspace directory
    2. captures stdout, stderr, and return code
    3. returns all three values

    Returns:
        Tuple of (returncode, stdout, stderr)

    Example:
        >>> returncode, stdout, stderr = run_command_in_workspace(
        ...     workspace_dir,
        ...     "python script.py"
        ... )
        >>> assert returncode == 0
    """
    command_parts = command.split()
    result = subprocess.run(
        command_parts,
        cwd=workspace_dir,
        capture_output=True,
        text=True,
        timeout=30,
    )

    return result.returncode, result.stdout, result.stderr
