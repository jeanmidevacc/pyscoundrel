"""Unit tests for pyscoundrel.logging.formatters"""

import json

import pytest

from pyscoundrel.logging.events import GameEvent
from pyscoundrel.logging.formatters import JSONFormatter, TextFormatter

pytestmark = pytest.mark.unit


@pytest.fixture
def basic_event():
    return GameEvent(
        event="damage_taken",
        timestamp="2024-01-15T14:30:00.123456",
        data={"monster": "Goblin", "damage": 3},
    )


@pytest.fixture
def event_with_state():
    return GameEvent(
        event="turn_end",
        timestamp="2024-01-15T14:30:00.123456",
        data={"turn": 2},
        state={
            "player": {"health": 12, "max_health": 20},
            "dungeon": {"count": 30},
            "discard": {"count": 10},
        },
    )


class TestJSONFormatter:
    def test_produces_valid_json(self, basic_event):
        formatter = JSONFormatter()
        output = formatter.format(basic_event)
        parsed = json.loads(output)
        assert isinstance(parsed, dict)

    def test_output_is_single_line(self, basic_event):
        formatter = JSONFormatter()
        output = formatter.format(basic_event)
        assert "\n" not in output

    def test_contains_event_type(self, basic_event):
        formatter = JSONFormatter()
        output = formatter.format(basic_event)
        assert "damage_taken" in output

    def test_contains_data(self, basic_event):
        formatter = JSONFormatter()
        parsed = json.loads(formatter.format(basic_event))
        assert parsed["data"]["damage"] == 3


class TestTextFormatter:
    def test_contains_event_name_uppercased(self, basic_event):
        formatter = TextFormatter()
        output = formatter.format(basic_event)
        assert "DAMAGE_TAKEN" in output

    def test_contains_time_component(self, basic_event):
        formatter = TextFormatter()
        output = formatter.format(basic_event)
        assert "14:30:00" in output

    def test_contains_data_key_value(self, basic_event):
        formatter = TextFormatter()
        output = formatter.format(basic_event)
        assert "damage=3" in output

    def test_contains_state_when_present(self, event_with_state):
        formatter = TextFormatter()
        output = formatter.format(event_with_state)
        assert "health=12/20" in output
        assert "dungeon=30" in output

    def test_no_state_line_when_absent(self, basic_event):
        formatter = TextFormatter()
        output = formatter.format(basic_event)
        assert "State:" not in output

    def test_formats_list_value_in_data(self):
        event = GameEvent(
            event="room_drawn",
            timestamp="2024-01-15T14:30:00.000000",
            data={"cards": ["Goblin", "Sword", "Potion"]},
        )
        output = TextFormatter().format(event)
        assert "cards=[Goblin, Sword, Potion]" in output

    def test_state_with_weapon_shows_weapon(self):
        event = GameEvent(
            event="turn_end",
            timestamp="2024-01-15T14:30:00.000000",
            data={},
            state={
                "player": {"health": 15, "max_health": 20, "weapon": {"card": "Iron Sword"}},
                "dungeon": {"count": 40},
                "discard": {"count": 4},
            },
        )
        output = TextFormatter().format(event)
        assert "weapon=Iron Sword" in output
