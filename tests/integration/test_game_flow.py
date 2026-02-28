"""Integration tests for the core game flow: engine + models + dungeon."""

import pytest

from pyscoundrel.game.state import GamePhase
from pyscoundrel.models.card import CardType

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _face_room(engine):
    """Face all 3 required cards in the current room, handling combat."""
    state = engine.state
    room = state.current_room
    while not room.is_complete and not engine.is_game_over:
        available = room.available_cards
        card = available[0]
        room_idx = room.cards.index(card)
        result = engine.face_card(room_idx)
        if result.metadata and "monster" in result.metadata:
            engine.fight_monster_barehanded(result.metadata["monster"])


# ---------------------------------------------------------------------------
# Game start and draw
# ---------------------------------------------------------------------------


class TestGameStart:
    def test_start_sets_draw_room_phase(self, engine):
        result = engine.start_game()
        assert result.success is True
        assert engine.state.phase == GamePhase.DRAW_ROOM

    def test_default_deck_has_44_cards(self, engine):
        assert engine.state.deck.remaining == 44

    def test_draw_room_produces_four_cards(self, engine):
        engine.start_game()
        engine.draw_room()
        assert len(engine.state.current_room.cards) == 4

    def test_draw_room_reduces_deck_by_4(self, engine):
        engine.start_game()
        before = engine.state.deck.remaining
        engine.draw_room()
        assert engine.state.deck.remaining == before - 4

    def test_draw_room_sets_decide_avoid_phase(self, engine):
        engine.start_game()
        engine.draw_room()
        assert engine.state.phase == GamePhase.DECIDE_AVOID

    def test_cannot_draw_room_before_start(self, engine):
        result = engine.draw_room()
        assert result.success is False


# ---------------------------------------------------------------------------
# Facing cards
# ---------------------------------------------------------------------------


class TestFacingCards:
    def test_facing_card_adds_to_cards_faced(self, started_engine):
        room = started_engine.state.current_room
        card = room.available_cards[0]
        room_idx = room.cards.index(card)
        result = started_engine.face_card(room_idx)
        if result.metadata and "monster" in result.metadata:
            started_engine.fight_monster_barehanded(result.metadata["monster"])
        assert len(room.cards_faced) == 1

    def test_facing_three_cards_completes_room(self, started_engine):
        _face_room(started_engine)
        assert started_engine.state.current_room.is_complete is True

    def test_room_has_one_card_remaining_after_complete(self, started_engine):
        _face_room(started_engine)
        assert started_engine.state.current_room.get_remaining_card() is not None

    def test_remaining_card_carried_into_next_room(self, started_engine):
        _face_room(started_engine)
        leftover = started_engine.state.current_room.get_remaining_card()
        started_engine.draw_room()
        new_room = started_engine.state.current_room
        assert leftover in new_room.cards

    def test_next_room_draws_three_new_cards(self, started_engine):
        _face_room(started_engine)
        deck_before = started_engine.state.deck.remaining
        started_engine.draw_room()
        assert started_engine.state.deck.remaining == deck_before - 3

    def test_cannot_face_card_in_wrong_phase(self, engine):
        engine.start_game()
        result = engine.face_card(0)
        assert result.success is False


# ---------------------------------------------------------------------------
# Avoid room
# ---------------------------------------------------------------------------


class TestAvoidRoom:
    def test_can_avoid_room_initially(self, started_engine):
        assert started_engine.state.can_avoid_room is True

    def test_avoid_room_puts_cards_back_in_deck(self, started_engine):
        deck_before = started_engine.state.deck.remaining
        started_engine.avoid_room()
        assert started_engine.state.deck.remaining == deck_before + 4

    def test_cannot_avoid_two_rooms_in_a_row(self, started_engine):
        started_engine.avoid_room()
        started_engine.draw_room()
        result = started_engine.avoid_room()
        assert result.success is False

    def test_can_avoid_again_after_facing_a_room(self, started_engine):
        started_engine.avoid_room()
        started_engine.draw_room()
        _face_room(started_engine)
        started_engine.draw_room()
        assert started_engine.state.can_avoid_room is True


# ---------------------------------------------------------------------------
# Weapon mechanic
# ---------------------------------------------------------------------------


class TestWeaponMechanic:
    def test_equipping_weapon_sets_player_weapon(self, engine):
        engine.start_game()
        # Build a deck that starts with a weapon card
        from pyscoundrel.models.card import Card

        weapon = Card.from_dungeon_card("sword_01", "Sword", CardType.WEAPON, 8)
        engine.state.deck._cards.insert(0, weapon)
        engine.state.deck._cards.insert(0, weapon)
        engine.state.deck._cards.insert(0, weapon)
        engine.state.deck._cards.insert(0, weapon)

        engine.draw_room()
        room = engine.state.current_room
        # Face the weapon
        weapon_idx = next(i for i, c in enumerate(room.cards) if c.card_type == CardType.WEAPON)
        engine.face_card(weapon_idx)
        assert engine.state.player.has_weapon is True

    def test_fighting_with_weapon_reduces_damage(self, engine):
        engine.start_game()
        # Inject a strong weapon and a weak monster so weapon absorbs all damage
        from pyscoundrel.models.card import Card

        strong_weapon = Card.from_dungeon_card("axe_01", "Axe", CardType.WEAPON, 14)
        weak_monster = Card.from_dungeon_card("rat_01", "Rat", CardType.MONSTER, 2)
        engine.state.deck._cards = [
            strong_weapon,
            weak_monster,
            weak_monster,
            weak_monster,
        ] + engine.state.deck._cards

        engine.draw_room()
        room = engine.state.current_room
        # Equip weapon
        w_idx = next(i for i, c in enumerate(room.cards) if c.card_type == CardType.WEAPON)
        engine.face_card(w_idx)

        # Fight a monster with the weapon — should take 0 damage (2 - 14 = 0)
        m_idx = next(
            i
            for i, c in enumerate(room.cards)
            if c.card_type == CardType.MONSTER and c not in room.cards_faced
        )
        result = engine.face_card(m_idx)
        monster = result.metadata["monster"]
        combat = engine.fight_monster_with_weapon(monster)
        assert combat.damage_taken == 0
        assert engine.state.player.health == 20


# ---------------------------------------------------------------------------
# Health potion
# ---------------------------------------------------------------------------


class TestHealthPotion:
    def test_using_potion_heals_player(self, engine):
        engine.start_game()
        engine.state.player.health = 10
        # Inject a potion
        from pyscoundrel.models.card import Card

        potion = Card.from_dungeon_card("p01", "Potion", CardType.HEALTH_POTION, 6)
        engine.state.deck._cards = [potion, potion, potion, potion] + engine.state.deck._cards

        engine.draw_room()
        room = engine.state.current_room
        p_idx = next(i for i, c in enumerate(room.cards) if c.card_type == CardType.HEALTH_POTION)
        engine.face_card(p_idx)
        assert engine.state.player.health == 16

    def test_second_potion_in_same_turn_is_discarded(self, engine):
        engine.start_game()
        engine.state.player.health = 5
        from pyscoundrel.models.card import Card

        # Use distinct card_ids so frozen-dataclass equality doesn't hide the second potion
        potion1 = Card.from_dungeon_card("p01", "Potion", CardType.HEALTH_POTION, 6)
        potion2 = Card.from_dungeon_card("p02", "Potion", CardType.HEALTH_POTION, 6)
        monster = Card.from_dungeon_card("m01", "Rat", CardType.MONSTER, 1)
        engine.state.deck._cards = [potion1, potion2, monster, monster] + engine.state.deck._cards

        engine.draw_room()
        room = engine.state.current_room
        # Face first potion
        p_idx = next(i for i, c in enumerate(room.cards) if c.card_type == CardType.HEALTH_POTION)
        engine.face_card(p_idx)
        health_after_first = engine.state.player.health

        # Face second potion — should be discarded (no extra heal)
        p_idx2 = next(
            i
            for i, c in enumerate(room.cards)
            if c.card_type == CardType.HEALTH_POTION and c not in room.cards_faced
        )
        engine.face_card(p_idx2)
        assert engine.state.player.health == health_after_first


# ---------------------------------------------------------------------------
# Game over conditions
# ---------------------------------------------------------------------------


class TestGameOver:
    def test_player_death_ends_game_as_loss(self, engine):
        engine.start_game()
        engine.state.player.health = 1
        from pyscoundrel.models.card import Card

        monster = Card.from_dungeon_card("boss_01", "Boss", CardType.MONSTER, 10)
        engine.state.deck._cards = [monster, monster, monster, monster] + engine.state.deck._cards

        engine.draw_room()
        room = engine.state.current_room
        m_idx = next(i for i, c in enumerate(room.cards) if c.card_type == CardType.MONSTER)
        result = engine.face_card(m_idx)
        engine.fight_monster_barehanded(result.metadata["monster"])

        assert engine.is_game_over is True
        assert engine.state.victory is False

    def test_score_negative_on_death(self, engine):
        engine.start_game()
        engine.state.player.health = 1
        from pyscoundrel.models.card import Card

        monster = Card.from_dungeon_card("boss_01", "Boss", CardType.MONSTER, 10)
        engine.state.deck._cards = [monster, monster, monster, monster] + engine.state.deck._cards

        engine.draw_room()
        room = engine.state.current_room
        m_idx = next(i for i, c in enumerate(room.cards) if c.card_type == CardType.MONSTER)
        result = engine.face_card(m_idx)
        engine.fight_monster_barehanded(result.metadata["monster"])

        assert engine.score < 0
