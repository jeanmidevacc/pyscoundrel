"""Unit tests for pyscoundrel.game.actions"""

import pytest

from pyscoundrel.game.actions import Action, ActionResult, ActionType

pytestmark = pytest.mark.unit


class TestActionType:
    def test_all_action_types_exist(self):
        expected = {
            "AVOID_ROOM",
            "FACE_CARD",
            "FIGHT_BAREHANDED",
            "FIGHT_WITH_WEAPON",
            "EQUIP_WEAPON",
            "USE_POTION",
            "START_TURN",
            "END_TURN",
        }
        assert {a.name for a in ActionType} == expected


class TestAction:
    def test_creates_action_with_type(self):
        action = Action(action_type=ActionType.AVOID_ROOM)
        assert action.action_type == ActionType.AVOID_ROOM

    def test_card_index_defaults_to_none(self):
        action = Action(action_type=ActionType.FACE_CARD)
        assert action.card_index is None

    def test_stores_card_index(self):
        action = Action(action_type=ActionType.FACE_CARD, card_index=2)
        assert action.card_index == 2

    def test_str_without_card_index(self):
        action = Action(action_type=ActionType.AVOID_ROOM)
        assert str(action) == "avoid_room"

    def test_str_with_card_index(self):
        action = Action(action_type=ActionType.FACE_CARD, card_index=1)
        assert "card=1" in str(action)

    def test_repr_format(self):
        action = Action(action_type=ActionType.FIGHT_BAREHANDED, card_index=0)
        assert "fight_barehanded" in repr(action)
        assert "card_index=0" in repr(action)


class TestActionResult:
    def test_success_stored(self):
        result = ActionResult(success=True, message="ok")
        assert result.success is True

    def test_message_stored(self):
        result = ActionResult(success=False, message="failed")
        assert result.message == "failed"

    def test_defaults_zero_damage_and_health(self):
        result = ActionResult(success=True, message="ok")
        assert result.damage_taken == 0
        assert result.health_gained == 0

    def test_is_fatal_falsy_with_no_metadata(self):
        # is_fatal returns None (not False) when metadata is absent — None is falsy
        result = ActionResult(success=True, message="ok")
        assert not result.is_fatal

    def test_is_fatal_false_when_player_not_dead(self):
        result = ActionResult(success=True, message="ok", metadata={"player_died": False})
        assert result.is_fatal is False

    def test_is_fatal_true_when_player_died(self):
        result = ActionResult(success=True, message="ok", metadata={"player_died": True})
        assert result.is_fatal is True

    def test_str_with_no_hp_changes(self):
        result = ActionResult(success=True, message="Moved")
        assert str(result) == "Moved"

    def test_str_shows_damage(self):
        result = ActionResult(success=True, message="Hit", damage_taken=3)
        assert "-3 HP" in str(result)

    def test_str_shows_health_gained(self):
        result = ActionResult(success=True, message="Healed", health_gained=5)
        assert "+5 HP" in str(result)
