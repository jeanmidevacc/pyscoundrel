"""Game event logger."""

from pathlib import Path
from typing import Any, Dict, Optional, TextIO

from .events import GameEvent, create_event
from .formatters import JSONFormatter, TextFormatter


class GameLogger:
    """Logger for game events."""

    def __init__(self, log_file: Optional[Path] = None, log_console: bool = False):
        """
        Initialize logger.

        Args:
            log_file: Path to log file (JSON format)
            log_console: Whether to log to console (text format)
        """
        self.log_file = log_file
        self.log_console = log_console

        self.json_formatter = JSONFormatter()
        self.text_formatter = TextFormatter()

        self._file_handle: Optional[TextIO] = None

        # Open log file if specified
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)
            self._file_handle = open(self.log_file, "w")

    def log_event(self, event: GameEvent) -> None:
        """Log an event."""
        # Write to file (JSON)
        if self._file_handle:
            json_line = self.json_formatter.format(event)
            self._file_handle.write(json_line + "\n")
            self._file_handle.flush()

        # Write to console (text)
        if self.log_console:
            text_line = self.text_formatter.format(event)
            print(text_line)

    def log(
        self, event_type: str, data: Dict[str, Any], state: Optional[Dict[str, Any]] = None
    ) -> None:
        """Create and log an event."""
        event = create_event(event_type, data, state)
        self.log_event(event)

    def close(self) -> None:
        """Close log file."""
        if self._file_handle:
            self._file_handle.close()
            self._file_handle = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        """Context manager exit."""
        self.close()
