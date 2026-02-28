# Dungeon Configuration

Dungeons are defined as YAML files. You can create custom card pools to build
themed experiences instead of using the default card set.

## YAML format

```yaml
version: "1.0"

cards:
  - id: "rat"           # unique identifier
    name: "Giant Rat"   # display name
    type: monster       # monster | weapon | health_potion
    value: 2            # damage / healing / weapon power
    count: 4            # copies in deck
    description: "..."  # optional
```

## Example dungeon

```yaml
version: "1.0"

cards:
  - { id: rat,       name: "Giant Rat",     type: monster,       value: 2,  count: 4 }
  - { id: zombie,    name: "Zombie",        type: monster,       value: 5,  count: 3 }
  - { id: vampire,   name: "Vampire Lord",  type: monster,       value: 12, count: 2 }
  - { id: stick,     name: "Wooden Stick",  type: weapon,        value: 3,  count: 2 }
  - { id: hammer,    name: "War Hammer",    type: weapon,        value: 7,  count: 2 }
  - { id: potion_s,  name: "Small Potion",  type: health_potion, value: 4,  count: 3 }
  - { id: potion_l,  name: "Large Potion",  type: health_potion, value: 8,  count: 2 }
```

## Using a custom dungeon

```bash
python -m pyscoundrel --dungeon path/to/dungeon.yaml
```

```python
from pathlib import Path
from pyscoundrel import Dungeon, GameEngine

dungeon = Dungeon(config_path=Path("my_dungeon.yaml"))
errors = dungeon.validate()
if errors:
    raise ValueError(errors)

engine = GameEngine(dungeon=dungeon, seed=42)
```

## Balance guidelines

- **Total cards**: 40–50 recommended
- **Monsters**: ~60% — mix of low (2–5), mid (6–10), high (11–13) values
- **Weapons**: ~20% — values 2–10
- **Potions**: ~20% — values 2–10

## Validation

`dungeon.validate()` returns a list of error strings. It checks for:

- Duplicate card IDs
- Non-positive values or counts
- Invalid card types
- Fewer than 20 total cards
