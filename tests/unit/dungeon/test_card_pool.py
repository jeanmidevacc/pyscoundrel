"""Unit tests for pyscoundrel.dungeon.card_pool"""

import pytest
from pathlib import Path
from pyscoundrel.dungeon.card_pool import CardDefinition, Dungeon
from pyscoundrel.models.card import CardType

pytestmark = pytest.mark.unit


@pytest.fixture
def fixtures_dir():
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def dungeon(fixtures_dir):
    return Dungeon(config_path=fixtures_dir / "minimal.yaml")


class TestCardDefinitionFromDict:
    def test_parses_monster(self):
        data = {"id": "g01", "name": "Goblin", "type": "monster", "value": 5, "count": 2}
        card_def = CardDefinition.from_dict(data)
        assert card_def.card_type == CardType.MONSTER
        assert card_def.value == 5
        assert card_def.count == 2

    def test_parses_weapon(self):
        data = {"id": "s01", "name": "Sword", "type": "weapon", "value": 8, "count": 1}
        card_def = CardDefinition.from_dict(data)
        assert card_def.card_type == CardType.WEAPON

    def test_parses_health_potion(self):
        data = {"id": "p01", "name": "Potion", "type": "health_potion", "value": 6, "count": 1}
        card_def = CardDefinition.from_dict(data)
        assert card_def.card_type == CardType.HEALTH_POTION

    def test_description_is_optional(self):
        data = {"id": "g01", "name": "Goblin", "type": "monster", "value": 5, "count": 1}
        card_def = CardDefinition.from_dict(data)
        assert card_def.description is None

    def test_description_stored_when_present(self):
        data = {
            "id": "g01",
            "name": "Goblin",
            "type": "monster",
            "value": 5,
            "count": 1,
            "description": "A small creature",
        }
        card_def = CardDefinition.from_dict(data)
        assert card_def.description == "A small creature"

    def test_raises_on_invalid_type(self):
        data = {"id": "x01", "name": "Unknown", "type": "dragon", "value": 10, "count": 1}
        with pytest.raises(ValueError, match="Invalid card type"):
            CardDefinition.from_dict(data)


class TestDungeonLoad:
    def test_loads_version(self, dungeon):
        assert dungeon.version == "1.0"

    def test_loads_card_definitions(self, dungeon):
        assert len(dungeon.card_definitions) == 3

    def test_raises_on_missing_file(self, fixtures_dir):
        with pytest.raises(FileNotFoundError):
            Dungeon(config_path=fixtures_dir / "nonexistent.yaml")

    def test_get_total_cards_sums_counts(self, dungeon):
        assert dungeon.get_total_cards() == 7  # 3 + 2 + 2

    def test_get_cards_by_type_monsters(self, dungeon):
        monsters = dungeon.get_cards_by_type(CardType.MONSTER)
        assert len(monsters) == 1
        assert monsters[0].id == "goblin_01"

    def test_get_cards_by_type_weapons(self, dungeon):
        weapons = dungeon.get_cards_by_type(CardType.WEAPON)
        assert len(weapons) == 1

    def test_get_card_by_id_found(self, dungeon):
        card = dungeon.get_card_by_id("sword_01")
        assert card is not None
        assert card.name == "Iron Sword"

    def test_get_card_by_id_not_found(self, dungeon):
        assert dungeon.get_card_by_id("nonexistent") is None


class TestDungeonValidate:
    def test_valid_dungeon_has_no_errors(self):
        # Use the bundled default dungeon, which has 44 cards and should be fully valid
        dungeon = Dungeon()
        errors = dungeon.validate()
        assert errors == []

    def test_detects_duplicate_ids(self, fixtures_dir):
        dungeon = Dungeon(config_path=fixtures_dir / "duplicate_ids.yaml")
        errors = dungeon.validate()
        assert any("Duplicate" in e for e in errors)

    def test_detects_non_positive_value(self, fixtures_dir):
        dungeon = Dungeon(config_path=fixtures_dir / "non_positive_value.yaml")
        errors = dungeon.validate()
        assert any("non-positive value" in e for e in errors)

    def test_detects_too_few_cards(self, dungeon):
        # minimal.yaml only has 7 total cards — below the 20 minimum
        errors = dungeon.validate()
        assert any("too few cards" in e for e in errors)

    def test_detects_non_positive_count(self, fixtures_dir):
        dungeon = Dungeon(config_path=fixtures_dir / "non_positive_count.yaml")
        errors = dungeon.validate()
        assert any("non-positive count" in e for e in errors)


class TestDungeonInvalidConfig:
    def test_malformed_yaml_raises(self, fixtures_dir):
        with pytest.raises(Exception):  # yaml.YAMLError or subclass
            Dungeon(config_path=fixtures_dir / "malformed.yaml")

    def test_missing_required_field_id_raises(self, fixtures_dir):
        with pytest.raises(KeyError):
            Dungeon(config_path=fixtures_dir / "missing_id.yaml")

    def test_missing_required_field_value_raises(self, fixtures_dir):
        with pytest.raises(KeyError):
            Dungeon(config_path=fixtures_dir / "missing_value.yaml")

    def test_missing_required_field_count_raises(self, fixtures_dir):
        with pytest.raises(KeyError):
            Dungeon(config_path=fixtures_dir / "missing_count.yaml")

    def test_invalid_card_type_string_raises(self, fixtures_dir):
        with pytest.raises(ValueError, match="Invalid card type"):
            Dungeon(config_path=fixtures_dir / "invalid_type.yaml")

    def test_empty_cards_section_gives_no_definitions(self, fixtures_dir):
        dungeon = Dungeon(config_path=fixtures_dir / "empty_cards.yaml")
        assert dungeon.card_definitions == []
