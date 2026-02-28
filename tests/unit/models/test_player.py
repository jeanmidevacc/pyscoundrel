"""Unit tests for pyscoundrel.models.player"""

import pytest

from pyscoundrel.models.player import Player

pytestmark = pytest.mark.unit


class TestPlayerInit:
    def test_default_health_is_20(self):
        assert Player().health == 20

    def test_default_max_health_is_20(self):
        assert Player().max_health == 20

    def test_no_weapon_on_init(self):
        assert Player().equipped_weapon is None

    def test_potions_used_zero_on_init(self):
        assert Player().potions_used_this_turn == 0


class TestPlayerTakeDamage:
    def test_reduces_health(self, player):
        player.take_damage(5)
        assert player.health == 15

    def test_health_does_not_go_below_zero(self, player):
        player.take_damage(999)
        assert player.health == 0

    def test_full_damage_applied(self, player):
        player.take_damage(20)
        assert player.health == 0


class TestPlayerHeal:
    def test_increases_health(self, player):
        player.take_damage(10)
        player.heal(4)
        assert player.health == 14

    def test_returns_actual_amount_healed(self, player):
        player.take_damage(10)
        healed = player.heal(4)
        assert healed == 4

    def test_health_does_not_exceed_max(self, player):
        player.heal(100)
        assert player.health == player.max_health

    def test_returns_zero_when_already_at_max(self, player):
        healed = player.heal(5)
        assert healed == 0

    def test_partial_heal_capped_at_max(self, player):
        player.take_damage(3)
        healed = player.heal(10)
        assert healed == 3
        assert player.health == player.max_health


class TestPlayerEquipWeapon:
    def test_equips_weapon(self, player, weapon):
        player.equip_weapon(weapon)
        assert player.equipped_weapon == weapon

    def test_returns_none_when_no_previous_weapon(self, player, weapon):
        old = player.equip_weapon(weapon)
        assert old is None

    def test_returns_old_weapon_when_replacing(self, player, weapon):
        from pyscoundrel.models.card import Card, CardType
        from pyscoundrel.models.weapon import Weapon

        player.equip_weapon(weapon)
        new_weapon = Weapon(card=Card.from_dungeon_card("axe_01", "Axe", CardType.WEAPON, 6))
        old = player.equip_weapon(new_weapon)
        assert old == weapon
        assert player.equipped_weapon == new_weapon


class TestPlayerResetTurnState:
    def test_resets_potions_used(self, player):
        player.potions_used_this_turn = 2
        player.reset_turn_state()
        assert player.potions_used_this_turn == 0


class TestPlayerProperties:
    def test_is_alive_when_health_positive(self, player):
        assert player.is_alive is True

    def test_is_dead_when_health_zero(self, player):
        player.take_damage(20)
        assert player.is_dead is True

    def test_is_alive_false_when_dead(self, player):
        player.take_damage(20)
        assert player.is_alive is False

    def test_has_weapon_false_initially(self, player):
        assert player.has_weapon is False

    def test_has_weapon_true_after_equip(self, player, weapon):
        player.equip_weapon(weapon)
        assert player.has_weapon is True


class TestPlayerStr:
    def test_str_without_weapon(self, player):
        output = str(player)
        assert "20/20" in output
        assert "None" in output

    def test_str_with_weapon(self, player, weapon):
        player.equip_weapon(weapon)
        output = str(player)
        assert "20/20" in output
        assert "None" not in output

    def test_repr_format(self, player):
        assert "Player" in repr(player)
        assert "health=20" in repr(player)
