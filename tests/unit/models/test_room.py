"""Unit tests for pyscoundrel.models.room"""

import pytest

from pyscoundrel.models.card import Card, CardType
from pyscoundrel.models.room import Room

pytestmark = pytest.mark.unit


@pytest.fixture
def four_cards(monster_card, weapon_card, potion_card):
    return [
        monster_card,
        weapon_card,
        potion_card,
        Card.from_dungeon_card("goblin_02", "Goblin 2", CardType.MONSTER, 3),
    ]


@pytest.fixture
def full_room(four_cards):
    room = Room()
    for card in four_cards:
        room.add_card(card)
    return room


class TestRoomAddCard:
    def test_adds_card_to_room(self, monster_card):
        room = Room()
        room.add_card(monster_card)
        assert monster_card in room.cards

    def test_adds_up_to_four_cards(self, four_cards):
        room = Room()
        for card in four_cards:
            room.add_card(card)
        assert len(room.cards) == 4

    def test_raises_when_full(self, full_room, potion_card):
        extra = Card.from_dungeon_card("extra_01", "Extra", CardType.MONSTER, 1)
        with pytest.raises(ValueError, match="already has 4 cards"):
            full_room.add_card(extra)


class TestRoomFaceCard:
    def test_returns_the_correct_card(self, full_room, four_cards):
        card = full_room.face_card(0)
        assert card == four_cards[0]

    def test_tracks_faced_card(self, full_room, four_cards):
        full_room.face_card(0)
        assert four_cards[0] in full_room.cards_faced

    def test_can_face_three_cards(self, full_room):
        full_room.face_card(0)
        full_room.face_card(1)
        full_room.face_card(2)
        assert len(full_room.cards_faced) == 3

    def test_raises_on_fourth_face_attempt(self, full_room):
        full_room.face_card(0)
        full_room.face_card(1)
        full_room.face_card(2)
        with pytest.raises(ValueError, match="Cannot face more than 3"):
            full_room.face_card(3)

    def test_raises_on_negative_index(self, full_room):
        with pytest.raises(IndexError):
            full_room.face_card(-1)

    def test_raises_on_out_of_bounds_index(self, full_room):
        with pytest.raises(IndexError):
            full_room.face_card(4)

    def test_raises_when_card_already_faced(self, full_room):
        full_room.face_card(0)
        with pytest.raises(ValueError, match="already been faced"):
            full_room.face_card(0)


class TestRoomGetRemainingCard:
    def test_returns_none_before_three_faced(self, full_room):
        full_room.face_card(0)
        full_room.face_card(1)
        assert full_room.get_remaining_card() is None

    def test_returns_unfaced_card_after_three_faced(self, full_room, four_cards):
        full_room.face_card(0)
        full_room.face_card(1)
        full_room.face_card(2)
        remaining = full_room.get_remaining_card()
        assert remaining == four_cards[3]

    def test_returns_none_when_no_cards_faced(self, full_room):
        assert full_room.get_remaining_card() is None


class TestRoomProperties:
    def test_is_full_when_four_cards(self, full_room):
        assert full_room.is_full is True

    def test_is_not_full_with_fewer_cards(self, monster_card):
        room = Room()
        room.add_card(monster_card)
        assert room.is_full is False

    def test_is_complete_after_three_faced(self, full_room):
        full_room.face_card(0)
        full_room.face_card(1)
        full_room.face_card(2)
        assert full_room.is_complete is True

    def test_is_not_complete_before_three_faced(self, full_room):
        full_room.face_card(0)
        assert full_room.is_complete is False

    def test_available_cards_excludes_faced(self, full_room, four_cards):
        full_room.face_card(0)
        available = full_room.available_cards
        assert four_cards[0] not in available
        assert four_cards[1] in available

    def test_num_cards_remaining(self, full_room):
        assert full_room.num_cards_remaining == 4
        full_room.face_card(0)
        assert full_room.num_cards_remaining == 3

    def test_str_shows_faced_cards_in_brackets(self, full_room, four_cards):
        full_room.face_card(0)
        output = str(full_room)
        assert f"[{four_cards[0].display_name}]" in output
        assert four_cards[1].display_name in output

    def test_repr_format(self, full_room):
        full_room.face_card(0)
        assert "Room" in repr(full_room)
        assert "cards=4" in repr(full_room)
        assert "faced=1" in repr(full_room)


class TestRoomGetRemainingCardEdgeCase:
    def test_returns_none_when_all_cards_are_equal(self):
        # Frozen dataclass equality: if all 4 cards are equal, facing 3 of them
        # causes the loop to find no "not in cards_faced" card — hits defensive fallback.
        from pyscoundrel.models.card import Card, CardType

        same_card = Card.from_dungeon_card("g01", "Goblin", CardType.MONSTER, 5)
        room = Room()
        for _ in range(4):
            room.add_card(same_card)
        room.cards_faced = [same_card, same_card, same_card]
        assert room.get_remaining_card() is None
