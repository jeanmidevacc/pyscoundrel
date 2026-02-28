"""Unit tests for pyscoundrel.models.weapon"""

import pytest

from pyscoundrel.models.card import Card, CardType
from pyscoundrel.models.weapon import Weapon

pytestmark = pytest.mark.unit


class TestWeaponInit:
    def test_creates_weapon_from_weapon_card(self, weapon_card):
        weapon = Weapon(card=weapon_card)
        assert weapon.card == weapon_card
        assert weapon.slain_monsters == []

    def test_raises_on_non_weapon_card(self, monster_card):
        with pytest.raises(ValueError, match="not a weapon"):
            Weapon(card=monster_card)

    def test_raises_on_potion_card(self, potion_card):
        with pytest.raises(ValueError, match="not a weapon"):
            Weapon(card=potion_card)


class TestWeaponProperties:
    def test_damage_equals_card_value(self, weapon):
        assert weapon.damage == weapon.card.value

    def test_last_kill_value_is_none_when_unused(self, weapon):
        assert weapon.last_kill_value is None

    def test_last_kill_value_after_kill(self, weapon, monster_card):
        weapon.attack(monster_card)
        assert weapon.last_kill_value == monster_card.value

    def test_last_kill_value_tracks_most_recent_kill(self, weapon, monster_card, weak_monster):
        weapon.attack(monster_card)
        weapon.attack(weak_monster)
        assert weapon.last_kill_value == weak_monster.value

    def test_max_kill_value_is_none_when_unused(self, weapon):
        assert weapon.max_kill_value is None

    def test_max_kill_value_equals_last_kill_value_when_used(self, weapon, monster_card):
        weapon.attack(monster_card)
        assert weapon.max_kill_value == weapon.last_kill_value

    def test_is_used_false_initially(self, weapon):
        assert weapon.is_used is False

    def test_is_used_true_after_attack(self, weapon, monster_card):
        weapon.attack(monster_card)
        assert weapon.is_used is True


class TestWeaponCanKill:
    def test_unused_weapon_can_kill_any_monster(self, weapon, strong_monster):
        assert weapon.can_kill(strong_monster) is True

    def test_used_weapon_can_kill_equal_value_monster(self, weapon, monster_card):
        weapon.attack(monster_card)
        equal = Card.from_dungeon_card(
            "goblin_02", "Goblin 2", CardType.MONSTER, monster_card.value
        )
        assert weapon.can_kill(equal) is True

    def test_used_weapon_can_kill_lower_value_monster(self, weapon, monster_card, weak_monster):
        weapon.attack(monster_card)
        assert weapon.can_kill(weak_monster) is True

    def test_used_weapon_cannot_kill_higher_value_monster(
        self, weapon, weak_monster, strong_monster
    ):
        weapon.attack(weak_monster)
        assert weapon.can_kill(strong_monster) is False

    def test_raises_on_non_monster_card(self, weapon, potion_card):
        with pytest.raises(ValueError, match="not a monster"):
            weapon.can_kill(potion_card)


class TestWeaponAttack:
    def test_damage_taken_is_zero_when_weapon_stronger(self, monster_card):
        strong_weapon = Weapon(card=Card.from_dungeon_card("axe_01", "Axe", CardType.WEAPON, 10))
        damage = strong_weapon.attack(monster_card)
        assert damage == 0

    def test_damage_taken_when_monster_stronger(self, weapon, strong_monster):
        # weapon value=8, monster value=12 → damage = 12 - 8 = 4
        damage = weapon.attack(strong_monster)
        assert damage == strong_monster.value - weapon.damage

    def test_damage_taken_equals_zero_minimum(self, monster_card):
        # weapon stronger than monster
        strong_weapon = Weapon(card=Card.from_dungeon_card("axe_01", "Axe", CardType.WEAPON, 10))
        damage = strong_weapon.attack(monster_card)
        assert damage >= 0

    def test_records_kill_in_slain_monsters(self, weapon, monster_card):
        weapon.attack(monster_card)
        assert monster_card in weapon.slain_monsters

    def test_raises_when_weapon_cannot_kill_monster(self, weapon, weak_monster, strong_monster):
        weapon.attack(weak_monster)
        with pytest.raises(ValueError):
            weapon.attack(strong_monster)


class TestWeaponStr:
    def test_str_unused(self, weapon):
        assert "unused" in str(weapon)

    def test_str_used_shows_max_kill(self, weapon, monster_card):
        weapon.attack(monster_card)
        assert str(monster_card.value) in str(weapon)
        assert "unused" not in str(weapon)

    def test_repr_format(self, weapon):
        assert "Weapon" in repr(weapon)
        assert "kills=0" in repr(weapon)
