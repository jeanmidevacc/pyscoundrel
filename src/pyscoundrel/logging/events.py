"""Event definitions for game logging."""

from dataclasses import dataclass
from typing import Any, Optional, Dict
from datetime import datetime


@dataclass
class GameEvent:
    """Base class for all game events."""

    event: str
    timestamp: str
    data: Dict[str, Any]
    state: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {"timestamp": self.timestamp, "event": self.event, "data": self.data}
        if self.state:
            result["state"] = self.state
        return result


def create_event(
    event_type: str, data: Dict[str, Any], state: Optional[Dict[str, Any]] = None
) -> GameEvent:
    """Create a game event with timestamp."""
    timestamp = datetime.now().isoformat()
    return GameEvent(event=event_type, timestamp=timestamp, data=data, state=state)
