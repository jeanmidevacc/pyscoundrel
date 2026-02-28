# Quick Start

## Installation

```bash
pip install pyscoundrel
```

## Play the game

```bash
# Basic game
python -m pyscoundrel

# Reproducible game with a fixed seed
python -m pyscoundrel --seed 42

# Skip title screen
python -m pyscoundrel --no-title

# Custom dungeon
python -m pyscoundrel --dungeon my_dungeon.yaml
```

## Game mechanics

| Card type | Effect |
|---|---|
| Monster | Deals damage equal to its value (2–14) |
| Weapon | Reduces monster damage; can only kill monsters ≤ last kill value |
| Potion | Heals up to 20 HP; one per turn |

**Each turn:**
1. Draw 4 cards → Room
2. Face 3 of 4 (1 carries to the next room)
3. You may avoid a room once (cards go to bottom of deck), but not twice in a row
4. **Win**: clear all cards — **Lose**: health reaches 0

## Programmatic usage

```python
from pyscoundrel import GameEngine

engine = GameEngine(seed=42)
engine.start_game()

while not engine.is_game_over:
    engine.draw_room()
    # face the first card in the room
    result = engine.face_card(0)
    # handle monsters, potions, weapons via result.metadata ...

print(f"Victory: {engine.state.victory}, Score: {engine.state.score}")
```

## Running an agent

```bash
python -m pyscoundrel --agent examples/smart_agent.py --headless
```

See [Writing Agents](../api/agents) for the `Agent` base class API.
