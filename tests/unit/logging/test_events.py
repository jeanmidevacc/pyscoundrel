"""Unit tests for pyscoundrel.logging.events"""

import pytest
from pyscoundrel.logging.events import GameEvent, create_event

pytestmark = pytest.mark.unit


class TestGameEvent:
    def test_to_dict_contains_required_keys(self):
        event = GameEvent(event="test_event", timestamp="2024-01-01T00:00:00", data={"key": "val"})
        result = event.to_dict()
        assert "timestamp" in result
        assert "event" in result
        assert "data" in result

    def test_to_dict_excludes_state_when_none(self):
        event = GameEvent(event="test_event", timestamp="2024-01-01T00:00:00", data={})
        result = event.to_dict()
        assert "state" not in result

    def test_to_dict_includes_state_when_present(self):
        event = GameEvent(
            event="test_event",
            timestamp="2024-01-01T00:00:00",
            data={},
            state={"player": {"health": 10}},
        )
        result = event.to_dict()
        assert "state" in result
        assert result["state"]["player"]["health"] == 10

    def test_to_dict_preserves_data(self):
        data = {"action": "fight", "damage": 5}
        event = GameEvent(event="combat", timestamp="2024-01-01T00:00:00", data=data)
        assert event.to_dict()["data"] == data


class TestCreateEvent:
    def test_creates_event_with_correct_type(self):
        event = create_event("game_started", {"seed": 42})
        assert event.event == "game_started"

    def test_creates_event_with_data(self):
        event = create_event("damage_taken", {"amount": 3})
        assert event.data["amount"] == 3

    def test_creates_event_with_timestamp(self):
        event = create_event("game_started", {})
        assert event.timestamp is not None
        assert "T" in event.timestamp  # ISO format contains T

    def test_creates_event_with_state(self):
        state = {"player": {"health": 15}}
        event = create_event("turn_end", {}, state=state)
        assert event.state == state

    def test_creates_event_without_state(self):
        event = create_event("game_started", {})
        assert event.state is None
