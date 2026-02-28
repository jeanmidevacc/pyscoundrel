"""Formatters for game event logging."""

import json

from .events import GameEvent


class JSONFormatter:
    """Format events as JSON lines."""

    def format(self, event: GameEvent) -> str:
        """Format event as single-line JSON."""
        return json.dumps(event.to_dict(), separators=(",", ":"))


class TextFormatter:
    """Format events as human-readable text."""

    def format(self, event: GameEvent) -> str:
        """Format event as text."""
        time = event.timestamp.split("T")[1].split(".")[0]  # HH:MM:SS

        # Format the data part
        data_parts = []
        for key, value in event.data.items():
            if isinstance(value, list):
                value_str = f"[{', '.join(map(str, value))}]"
            else:
                value_str = str(value)
            data_parts.append(f"{key}={value_str}")

        data_str = ", ".join(data_parts)

        # Add compact state info
        state_str = ""
        if event.state:
            player = event.state.get("player", {})
            dungeon = event.state.get("dungeon", {})
            discard = event.state.get("discard", {})

            state_parts = [
                f"health={player.get('health', '?')}/{player.get('max_health', 20)}",
                f"dungeon={dungeon.get('count', 0)}",
                f"discard={discard.get('count', 0)}",
            ]

            weapon = player.get("weapon")
            if weapon:
                state_parts.append(f"weapon={weapon.get('card', '?')}")

            state_str = f"\n           State: {', '.join(state_parts)}"

        return f"[{time}] {event.event.upper()} | {data_str}{state_str}"
