"""Unit tests for pyscoundrel.game.state"""

from unittest.mock import MagicMock, PropertyMock

import pytest

from pyscoundrel.game.state import GamePhase, GameState
from pyscoundrel.models.card import Card, CardType

pytestmark = pytest.mark.unit


def _make_deck(is_empty=False, remaining=44, cards=None):
    """Build a minimal mock Deck."""
    deck = MagicMock()
    type(deck).is_empty = PropertyMock(return_value=is_empty)
    type(deck).remaining = PropertyMock(return_value=remaining)
    deck.cards = cards or []
    return deck


@pytest.fixture
def mock_deck():
    return _make_deck()


@pytest.fixture
def state(player, mock_deck):
    return GameState(player=player, deck=mock_deck)


class TestGameStateInit:
    def test_starts_in_setup_phase(self, state):
        assert state.phase == GamePhase.SETUP

    def test_turn_number_zero(self, state):
        assert state.turn_number == 0

    def test_game_not_over(self, state):
        assert state.game_over is False

    def test_no_victory_initially(self, state):
        assert state.victory is False


class TestCanAvoidRoom:
    def test_can_avoid_when_no_consecutive_avoids(self, state):
        assert state.can_avoid_room is True

    def test_cannot_avoid_after_one_consecutive_avoid(self, state):
        state.rooms_avoided_consecutively = 1
        assert state.can_avoid_room is False


class TestScore:
    def test_score_zero_when_game_ongoing(self, state):
        assert state.score == 0

    def test_score_equals_player_health_on_victory(self, state):
        state.game_over = True
        state.victory = True
        state.player.health = 14
        assert state.score == 14

    def test_score_negative_on_defeat(self, player):
        monster = Card.from_dungeon_card("goblin_01", "Goblin", CardType.MONSTER, 7)
        deck = _make_deck(remaining=1, cards=[monster])
        state = GameState(player=player, deck=deck)
        state.game_over = True
        state.victory = False
        assert state.score == -7

    def test_score_ignores_non_monsters_on_defeat(self, player):
        weapon = Card.from_dungeon_card("sword_01", "Sword", CardType.WEAPON, 8)
        deck = _make_deck(remaining=1, cards=[weapon])
        state = GameState(player=player, deck=deck)
        state.game_over = True
        state.victory = False
        assert state.score == 0


class TestDiscard:
    def test_appends_cards_to_discard_pile(self, state, monster_card):
        state.discard([monster_card])
        assert monster_card in state.discard_pile

    def test_appends_multiple_cards(self, state, monster_card, weapon_card):
        state.discard([monster_card, weapon_card])
        assert len(state.discard_pile) == 2


class TestStartNewTurn:
    def test_increments_turn_number(self, state):
        state.start_new_turn()
        assert state.turn_number == 1

    def test_resets_last_card_was_potion(self, state):
        state.last_card_was_potion = True
        state.start_new_turn()
        assert state.last_card_was_potion is False

    def test_resets_player_turn_state(self, state):
        state.player.potions_used_this_turn = 2
        state.start_new_turn()
        assert state.player.potions_used_this_turn == 0


class TestEndTurn:
    def test_sets_phase_to_turn_complete(self, state):
        state.end_turn()
        assert state.phase == GamePhase.TURN_COMPLETE


class TestMarkQuit:
    def test_sets_game_over(self, state):
        state.mark_quit()
        assert state.game_over is True

    def test_sets_victory_false(self, state):
        state.mark_quit()
        assert state.victory is False

    def test_sets_phase_to_game_over(self, state):
        state.mark_quit()
        assert state.phase == GamePhase.GAME_OVER


class TestCheckGameOver:
    def test_returns_false_when_game_ongoing(self, state):
        assert state.check_game_over() is False

    def test_returns_true_and_marks_loss_when_player_dead(self, state):
        state.player.take_damage(20)
        result = state.check_game_over()
        assert result is True
        assert state.game_over is True
        assert state.victory is False

    def test_returns_true_and_marks_victory_when_deck_empty(self, player):
        deck = _make_deck(is_empty=True)
        state = GameState(player=player, deck=deck)
        result = state.check_game_over()
        assert result is True
        assert state.game_over is True
        assert state.victory is True

    def test_sets_game_over_phase_on_death(self, state):
        state.player.take_damage(20)
        state.check_game_over()
        assert state.phase == GamePhase.GAME_OVER
