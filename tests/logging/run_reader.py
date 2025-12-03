import json
from pathlib import Path
from typing import Any


class TestRunLog:
    """Read and analyze test run logs."""

    def __init__(self, log_dir: Path):
        """Initialize from log directory."""

        self.log_dir = log_dir
        self.metadata = self._load_metadata()
        self.events = self._load_events()
        self.command_outputs = self._load_command_outputs()

    @classmethod
    def load(cls, log_dir: str | Path) -> "TestRunLog":
        """Load test run log from directory."""

        return cls(Path(log_dir))

    def _load_metadata(self) -> dict[str, Any]:
        """Load metadata.json."""

        with open(self.log_dir / "metadata.json") as f:
            return json.load(f)  # type: ignore[no-any-return]

    def _load_events(self) -> list[dict[str, Any]]:
        """Load events from events.jsonl."""

        events = []
        events_file = self.log_dir / "events.jsonl"
        if events_file.exists():
            with open(events_file) as f:
                for line in f:
                    events.append(json.loads(line))
        return events

    def _load_command_outputs(self) -> list[Path]:
        """Get list of command output files."""

        output_dir = self.log_dir / "command_outputs"
        if output_dir.exists():
            return sorted(output_dir.glob("*.txt"))
        return []
